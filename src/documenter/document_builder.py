from pathlib import Path
import subprocess

from src.documenter.lm_integration import generate_diagram_description
from src.documenter.uml_generator import compile_plantuml


def build_document_bundle(base_dir: Path, plan, model, kb):

    docs_dir = base_dir / "docs" / "generated"
    diagrams_dir = docs_dir / "diagrams"

    docs_dir.mkdir(parents=True, exist_ok=True)
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    output_md = docs_dir / "documentation.md"
    output_pdf = docs_dir / "documentation.pdf"

    # ----------------------------------------------------------
    # Se manca PNG prova a compilarlo dal PUML
    # ----------------------------------------------------------
    def ensure_png(diagram_type: str) -> bool:
        puml = diagrams_dir / f"{diagram_type}.puml"
        png = diagrams_dir / f"{diagram_type}.png"

        if png.exists():
            return True

        if puml.exists():
            try:
                compile_plantuml(puml)
                return png.exists()
            except Exception:
                return False

        return False

    diagram_titles = {
        "context_view": "Diagramma del Contesto",
        "logical_view": "Diagramma dei Componenti",
        "deployment_view": "Diagramma del Deployment",
        "runtime_view": "Diagramma di Sequenza",
        "security_view": "Diagramma di Sicurezza",
    }

    fallback_descriptions = {
        "context_view": "Il diagramma del contesto rappresenta il sistema e le interazioni con attori esterni.",
        "logical_view": "Il diagramma mostra la suddivisione del sistema in microservizi indipendenti.",
        "deployment_view": "Il diagramma illustra la distribuzione dei componenti su nodi infrastrutturali.",
        "runtime_view": "Il diagramma descrive il flusso temporale delle operazioni principali.",
        "security_view": "Il diagramma evidenzia le misure di sicurezza e i confini di trust.",
    }

    lines = []
    lines.append("# Documentazione Architetturale\n")
    lines.append("---\n")

    # ==========================================================
    # 1. INTRODUZIONE
    # ==========================================================

    lines.append("## 1. Introduzione\n")
    lines.append(
        f"La presente documentazione descrive in modo completo l’architettura **{model.id}**, "
        "progettata per operare in un contesto ad alta variabilità di carico, con requisiti "
        "stringenti in termini di scalabilità, sicurezza, affidabilità e manutenibilità.\n"
    )
    lines.append(
        "L’obiettivo è fornire una descrizione architetturale strutturata conforme ai principi "
        "IEEE 1016, includendo requisiti, driver architetturali, alternative considerate, "
        "trade-off e rappresentazioni UML.\n"
    )

    lines.append("\n---\n")

    # ==========================================================
    # 2. CONTESTO
    # ==========================================================

    lines.append("## 2. Contesto e Problema\n")
    lines.append(
        "Il sistema deve sostenere utenti concorrenti, transazioni sicure e integrazione "
        "con sistemi esterni garantendo scalabilità, resilienza e disponibilità continua.\n"
    )

    lines.append("\n---\n")

    # ==========================================================
    # 3. REQUISITI
    # ==========================================================

    lines.append("## 3. Requisiti del Sistema\n")

    lines.append("### 3.1 Requisiti Funzionali\n")
    lines.append(
        "Il sistema deve supportare le seguenti funzionalità principali:\n\n"
        "- **Gestione del catalogo prodotti**: inserimento, aggiornamento e consultazione prodotti.\n\n"
        "- **Ricerca e navigazione prodotti**: filtri avanzati e ricerca per parole chiave.\n\n"
        "- **Gestione del carrello**: aggiunta, modifica e rimozione prodotti.\n\n"
        "- **Creazione e gestione ordini**: conferma acquisto e tracciamento stato.\n\n"
        "- **Integrazione con gateway di pagamento**: elaborazione sicura delle transazioni.\n\n"
        "- **Integrazione con servizi di spedizione**: gestione consegne e aggiornamenti.\n\n"
        "- **Gestione account utente**: autenticazione, autorizzazione e gestione profilo.\n"
    )

    lines.append("\n### 3.2 Requisiti Non Funzionali\n")
    lines.append(
        "**Performance**: tempo di risposta ridotto per operazioni critiche.\n\n"
        "**Scalabilità**: supporto a elevati volumi di utenti concorrenti.\n\n"
        "**Disponibilità**: elevato uptime tramite ridondanza.\n\n"
        "**Sicurezza**: cifratura dati e controlli di accesso.\n\n"
        "**Manutenibilità**: evoluzione con impatto minimo.\n"
    )

    lines.append("\n---\n")

    # ==========================================================
    # 4. TRADE-OFF
    # ==========================================================

    lines.append("## 4. Trade-Off Architetturali\n")
    lines.append(
        "### Performance vs Complessità\n"
        "Un’architettura distribuita migliora la scalabilità ma aumenta la complessità operativa.\n\n"
        "### Disponibilità vs Costi\n"
        "La ridondanza migliora l’affidabilità ma incrementa i costi infrastrutturali.\n\n"
        "### Sicurezza vs Performance\n"
        "I controlli di sicurezza introducono overhead ma garantiscono protezione dei dati.\n"
    )

    # ==========================================================
    # 5. SEZIONE DIAGRAMMI
    # ==========================================================

    lines.append("\n---\n")
    lines.append("# SEZIONE DIAGRAMMI\n")

    section = 5

    for view in plan.views:

        diagram_type = kb.view_to_diagram_mapping.get(view)
        title = diagram_titles.get(view, view)

        lines.append("\n---\n")
        lines.append(f"## {section}. {title}\n")

        # Sempre ordine: Titolo → Immagine → Descrizione
        if diagram_type and ensure_png(diagram_type):
            lines.append(f"![{title}](diagrams/{diagram_type}.png)\n")
        else:
            lines.append("_Diagramma non disponibile_\n")

        try:
            desc = generate_diagram_description(model, view)
            if not desc.strip():
                desc = fallback_descriptions.get(view, "")
        except Exception:
            desc = fallback_descriptions.get(view, "")

        lines.append(desc + "\n")

        section += 1

    # ==========================================================
    # 6. CONCLUSIONI
    # ==========================================================

    lines.append("\n---\n")
    lines.append(f"## {section}. Conclusioni\n")
    lines.append(
        f"L’architettura **{model.id}** rappresenta una soluzione equilibrata tra "
        "scalabilità, sicurezza e manutenibilità, fornendo una base solida "
        "per evoluzione futura e deployment distribuito.\n"
    )

    # ==========================================================
    # SCRITTURA MARKDOWN
    # ==========================================================

    output_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"[DOCUMENT BUILT] {output_md}")

    # ==========================================================
    # GENERAZIONE PDF
    # ==========================================================

    try:
        subprocess.run(
            [
                "pandoc",
                str(output_md),
                "-o",
                str(output_pdf),
                "--pdf-engine=xelatex",
                "--resource-path",
                str(docs_dir),
            ],
            check=True,
        )
        print(f"[PDF GENERATED] {output_pdf}")
    except Exception as e:
        print("[WARNING] PDF generation failed:", e)
