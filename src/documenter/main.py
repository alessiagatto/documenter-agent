from src.documenter.planner import create_documentation_plan
from src.documenter.uml_generator import generate_component_diagram
from src.documenter.models import ArchitectureModel
import json
from pathlib import Path


def load_architecture(path: str) -> dict:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def list_available_architectures(data: dict) -> list:
    return [arch["architecture_id"] for arch in data.get("architectural_views", [])]


def select_architecture(data: dict, architecture_id: str) -> dict:
    for arch in data.get("architectural_views", []):
        if arch["architecture_id"] == architecture_id:
            return arch

    raise ValueError(f"Architecture '{architecture_id}' not found.")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    input_path = BASE_DIR / "data" / "input" / "finalArchitecture.json"

    architecture_data = load_architecture(input_path)

    # 🔹 Elenco architetture disponibili
    available = list_available_architectures(architecture_data)
    print("Available architectures:")
    for arch in available:
        print(f"- {arch}")

    # 🔹 Selezione architettura
    selected_id = "Microservices Architecture"
    selected_architecture = select_architecture(architecture_data, selected_id)
    selected_model = ArchitectureModel(selected_architecture)

    print(f"\nSelected architecture: {selected_model.id}")

    # 🔹 Pianificazione documentazione
    plan = create_documentation_plan(selected_model)

    print("\nDocumentation Plan:")
    for view in plan.views:
        print(f"- {view}")

    # 🔹 Componenti logical view
    components = selected_model.get_logical_components()
    print("\nLogical view components:")
    for comp in components:
        print(f"- {comp.id}")

    # 🔹 Connettori logical view
    connectors = selected_model.get_logical_connectors()
    print("\nLogical view connectors:")
    for conn in connectors:
        print(f"- {conn.source} -> {conn.target} ({conn.type})")

    # 🔹 Generazione diagramma
    output_file = BASE_DIR / "docs" / "generated" / "component_diagram.puml"
    generate_component_diagram(selected_model, output_file)

    print(f"\nComponent diagram generated at: {output_file}")