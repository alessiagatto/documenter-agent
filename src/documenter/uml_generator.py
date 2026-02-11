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
