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