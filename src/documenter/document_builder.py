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

    # --- Se manca PNG prova a compilarlo dal PUML
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
        "runtime_view": "Il diagramma descrive il flusso temporale delle operazioni durante il processo principale.",
        "security_view": "Il diagramma evidenzia le misure di sicurezza e i confini di trust.",
    }

    lines = []
    lines.append("# Documentazione Architetturale\n")
    lines.append("---\n")

    # ================= INTRODUZIONE =================

    lines.append("## 1. Introduzione\n")
    lines.append(
        "La presente documentazione descrive in modo completo l’architettura di un sistema "
        "progettato per operare in un contesto ad alta variabilità di carico, con requisiti "
        "stringenti in termini di scalabilità, sicurezza, affidabilità e manutenibilità.\n"
    )
    lines.append(
        "L’obiettivo è fornire una descrizione architetturale strutturata conforme ai principi IEEE 1016.\n"
    )

    lines.append("---\n")
    lines.append("## 2. Contesto e Problema\n")
    lines.append(
        "Il sistema deve sostenere utenti concorrenti, transazioni sicure e integrazione "
        "con sistemi esterni garantendo scalabilità e resilienza.\n"
    )

    lines.append("---\n")
    lines.append("## 3. Requisiti Funzionali\n")
    lines.append(
        "- Gestione catalogo prodotti\n"
        "- Ricerca e filtraggio\n"
        "- Gestione carrello\n"
        "- Creazione ordini\n"
        "- Integrazione pagamenti\n"
        "- Integrazione spedizioni\n"
        "- Gestione account utente\n"
    )

    lines.append("---\n")
    lines.append("## 4. Trade-Off Architetturali\n")
    lines.append(
        "Performance vs Complessità\n\n"
        "Disponibilità vs Costi\n\n"
        "Sicurezza vs Performance\n"
    )

    # ================= DIAGRAMMI =================

    lines.append("\n---\n")
    lines.append("# SEZIONE DIAGRAMMI\n")

    section = 5

    for view in plan.views:

        diagram_type = kb.view_to_diagram_mapping.get(view)
        title = diagram_titles.get(view, view)

        lines.append("\n---\n")
        lines.append(f"## {section}. {title}\n")

        # 🔥 SEMPRE TITOLO → IMMAGINE → DESCRIZIONE
        image_written = False

        if diagram_type and ensure_png(diagram_type):
            lines.append(f"![{title}](diagrams/{diagram_type}.png)\n")
            image_written = True

        if not image_written:
            lines.append("_Diagramma non disponibile_\n")

        # Descrizione LLM + fallback
        try:
            desc = generate_diagram_description(model, view)
            if not desc or not desc.strip():
                desc = fallback_descriptions.get(view, "")
        except Exception:
            desc = fallback_descriptions.get(view, "")

        lines.append(desc + "\n")

        section += 1

    # ================= CONCLUSIONI =================

    lines.append("\n---\n")
    lines.append(f"## {section}. Conclusioni\n")
    lines.append(
        f"L’architettura **{model.id}** rappresenta una soluzione equilibrata tra "
        "scalabilità, sicurezza e manutenibilità, fornendo una base solida per evoluzione futura.\n"
    )

    output_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"[DOCUMENT BUILT] {output_md}")

    # ================= PDF =================

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