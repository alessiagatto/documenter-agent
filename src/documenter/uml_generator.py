from pathlib import Path
from src.documenter.models import ArchitectureModel


def generate_component_diagram(model: ArchitectureModel, output_path: Path):
    components = model.get_logical_components()
    connectors = model.get_logical_connectors()

    lines = []
    lines.append("@startuml")
    lines.append("skinparam componentStyle rectangle")
    lines.append("")

    # Components
    for comp in components:
        lines.append(f'component "{comp.id}"')

    lines.append("")

    # Connectors
    for conn in connectors:
        if conn.source and conn.target:
            lines.append(f'"{conn.source}" --> "{conn.target}" : {conn.type}')

    lines.append("@enduml")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def generate_deployment_diagram(model: ArchitectureModel, output_path: Path):
    deployment_view = model.get_view("deployment_view")

    nodes = deployment_view.get("nodes", [])
    component_mapping = deployment_view.get("component_mapping", {})

    lines = []
    lines.append("@startuml")
    lines.append("skinparam nodeStyle rectangle")
    lines.append("")

    # Nodes
    for node in nodes:
        if isinstance(node, dict):
            node_name = node.get("name")
            lines.append(f'node "{node_name}" {{')
            for comp in node.get("components", []):
                lines.append(f'  component "{comp}"')
            lines.append("}")
        else:
            lines.append(f'node "{node}"')

    lines.append("")

    # Component mapping (per architetture che usano mapping separato)
    for comp, node in component_mapping.items():
        lines.append(f'"{comp}" --> "{node}"')

    lines.append("@enduml")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def generate_context_diagram(architecture_model, output_file):
    """
    Funzione per generare un diagramma di contesto.
    """
    with open(output_file, "w") as file:
        # Iniziamo a scrivere il diagramma in formato PlantUML
        file.write("@startuml\n")
        file.write("!define RECTANGLE class\n")
        file.write("\n")
        
        # Aggiungiamo componenti per il diagramma di contesto (puoi personalizzare)
        components = architecture_model.get_logical_components()
        for component in components:
            file.write(f"RECTANGLE {component.id}\n")
        
        # Aggiungi le relazioni (se ci sono)
        connectors = architecture_model.get_logical_connectors()
        for conn in connectors:
            file.write(f"{conn.source} --> {conn.target}\n")
        
        # Terminiamo il diagramma
        file.write("@enduml\n")

def generate_sequence_diagram(architecture_model, output_file):
    """
    Funzione per generare un diagramma di sequenza.
    """
    with open(output_file, "w") as file:
        file.write("@startuml\n")
        file.write("participant User\n")
        file.write("participant Cart Service\n")
        file.write("participant Order Service\n")
        file.write("participant Payment Service\n")
        file.write("participant Shipping Service\n")
        
        # Aggiungi le interazioni tra i componenti (sequenze di messaggi)
        file.write("User -> Cart Service: Add item to cart\n")
        file.write("Cart Service -> Order Service: Create order\n")
        file.write("Order Service -> Payment Service: Process payment\n")
        file.write("Order Service -> Shipping Service: Generate shipping label\n")
        
        file.write("@enduml\n")

def generate_security_diagram(architecture_model, output_file):
    """
    Funzione per generare un diagramma di sicurezza.
    """
    with open(output_file, "w") as file:
        file.write("@startuml\n")
        file.write("actor User\n")
        file.write("entity \"Web Server\" as WebServer\n")
        file.write("entity \"Application Server\" as AppServer\n")
        file.write("entity \"Database Server\" as DBServer\n")
        
        # Aggiungi interazioni di sicurezza tra i componenti
        file.write("User -> WebServer: Request\n")
        file.write("WebServer -> AppServer: Forward request\n")
        file.write("AppServer -> DBServer: Access database\n")
        file.write("AppServer -> WebServer: Return response\n")
        file.write("WebServer -> User: Return response\n")
        
        # Aggiungi misure di sicurezza come la cifratura e i controlli
        file.write("note right of WebServer\n")
        file.write("SSL/TLS encryption\n")
        file.write("end note\n")
        
        file.write("@enduml\n")