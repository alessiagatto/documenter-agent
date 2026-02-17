import requests

LM_API_URL = "http://127.0.0.1:1234"


def generate_diagram_description(model, view: str) -> str:
    """
    Descrizione robusta:
    - Non dipende dall'LLM per forza
    - Usa info del modello (components/connectors)
    - Sempre in italiano
    """

    # componenti e connessioni
    try:
        comps = model.get_logical_components()
    except Exception:
        comps = []

    try:
        conns = model.get_logical_connectors()
    except Exception:
        conns = []

    comp_names = []
    for c in comps:
        # nel tuo modello i componenti sembrano oggetti con .id
        name = getattr(c, "id", str(c))
        comp_names.append(name)

    conn_lines = []
    for conn in conns[:12]:  # limita per non fare un poema
        s = getattr(conn, "source", "")
        t = getattr(conn, "target", "")
        typ = getattr(conn, "type", "interazione")
        if s and t:
            conn_lines.append(f"- {s} → {t} ({typ})")

    if view == "context_view":
        return (
            "Il diagramma del contesto rappresenta il sistema come **black-box** e mostra gli attori/sistemi esterni "
            "con cui interagisce. È utile per chiarire **confini**, **responsabilità** e integrazioni con provider esterni "
            "(es. pagamenti e spedizioni)."
        )

    if view == "logical_view":
        testo = (
            "Il diagramma dei componenti mostra la scomposizione logica del sistema in servizi/moduli. "
            "Nel caso corrente sono presenti i seguenti elementi principali:\n\n"
            + "\n".join([f"- {n}" for n in comp_names]) +
            "\n\nLe dipendenze principali (parziali) sono:\n"
            + ("\n".join(conn_lines) if conn_lines else "- (dipendenze non disponibili)")
        )
        return testo

    if view == "deployment_view":
        return (
            "Il diagramma di deployment rappresenta la distribuzione fisica dei componenti su nodi infrastrutturali "
            "(es. web/app/database). Serve a evidenziare **separazione dei livelli**, scalabilità e isolamento dei failure. "
            "È utile anche per discutere aspetti di rete, bilanciamento e fault tolerance."
        )

    if view == "runtime_view":
        return (
            "Il diagramma di sequenza descrive il comportamento dinamico del sistema, evidenziando l’ordine temporale "
            "delle interazioni tra attore e servizi. In un contesto e-commerce tipicamente include: consultazione catalogo, "
            "gestione carrello, creazione ordine, pagamento e avvio spedizione."
        )

    if view == "security_view":
        return (
            "Il diagramma di sicurezza evidenzia i principali confini di fiducia (trust boundaries) e le misure di protezione: "
            "TLS in transito, autenticazione/autorizzazione, validazione input, logging e auditing. "
            "È utile per ragionare su threat model e punti critici (pagamenti, dati utenti)."
        )

    return "Descrizione non disponibile per questa vista."