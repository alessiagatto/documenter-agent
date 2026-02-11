from src.documenter.uml_generator import generate_deployment_diagram
from src.documenter.kb_loader import load_knowledge_base
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

    # 🔹 Caricamento Knowledge Base
    kb_path = BASE_DIR / "data" / "kb" / "documentation_rules.json"
    kb = load_knowledge_base(kb_path)

    print("\nKnowledge Base loaded.")
    print("View to diagram mapping:")
    for view, diagram in kb.view_to_diagram_mapping.items():
        print(f"- {view} -> {diagram}")

    # 🔹 Caricamento architettura
    input_path = BASE_DIR / "data" / "input" / "finalArchitecture.json"
    architecture_data = load_architecture(input_path)

    # 🔹 Elenco architetture disponibili
    available = list_available_architectures(architecture_data)
    print("\nAvailable architectures:")
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

    # 🔹 Componenti
    components = selected_model.get_logical_components()
    print("\nLogical view components:")
    for comp in components:
        print(f"- {comp.id}")

    # 🔹 Connettori
    connectors = selected_model.get_logical_connectors()
    print("\nLogical view connectors:")
    for conn in connectors:
        print(f"- {conn.source} -> {conn.target} ({conn.type})")

    # 🔹 Controllo layout intelligente
    max_components = kb.layout_rules.get("max_components_per_view", 10)

    components = selected_model.get_logical_components()

    if len(components) > max_components:
        print("\n[LAYOUT WARNING]")
        print(f"Logical view has {len(components)} components.")
        print("It exceeds max_components_per_view.")
        print("Consider splitting into multiple diagrams.")
    else:
        print("\nLayout check passed.")

    generated_files = []

for view in plan.views:
    diagram_type = kb.view_to_diagram_mapping.get(view)

    print(f"\n[DEBUG] View: {view}")
    print(f"[DEBUG] Diagram type from KB: {diagram_type}")

    if diagram_type == "component_diagram":
        output_file = BASE_DIR / "docs" / "generated" / f"{diagram_type}.puml"
        generate_component_diagram(selected_model, output_file)
        generated_files.append(output_file)

    elif diagram_type == "deployment_diagram":
        output_file = BASE_DIR / "docs" / "generated" / f"{diagram_type}.puml"
        generate_deployment_diagram(selected_model, output_file)
        generated_files.append(output_file)

    else:
        print(f"[INFO] Diagram type '{diagram_type}' not yet implemented.")

print("\nGenerated artifacts:")
for file in generated_files:
    print(f"- {file}")