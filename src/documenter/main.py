from src.documenter.vision_analyzer import analyze_diagram
from src.documenter.uml_generator import (
    generate_security_diagram,
    generate_sequence_diagram,
    generate_context_diagram,
    generate_deployment_diagram,
    generate_component_diagram,
    regenerate_sequence_with_feedback,
    compile_plantuml
)
from src.documenter.lm_integration import generate_description
from src.documenter.document_builder import build_document_bundle
from src.documenter.kb_loader import load_knowledge_base
from src.documenter.planner import create_documentation_plan
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

    # -----------------------------
    # 1️⃣ Load Knowledge Base
    # -----------------------------
    kb_path = BASE_DIR / "data" / "kb" / "documentation_rules.json"
    kb = load_knowledge_base(kb_path)

    print("\nKnowledge Base loaded.")
    print("View to diagram mapping:")
    for view, diagram in kb.view_to_diagram_mapping.items():
        print(f"- {view} -> {diagram}")

    # -----------------------------
    # 2️⃣ Load Architecture
    # -----------------------------
    input_path = BASE_DIR / "data" / "input" / "finalArchitecture.json"
    architecture_data = load_architecture(input_path)

    available = list_available_architectures(architecture_data)
    print("\nAvailable architectures:")
    for arch in available:
        print(f"- {arch}")

    selected_id = "Microservices Architecture"
    selected_architecture = select_architecture(architecture_data, selected_id)
    selected_model = ArchitectureModel(selected_architecture)

    print(f"\nSelected architecture: {selected_model.id}")

    # -----------------------------
    # 3️⃣ Documentation Plan
    # -----------------------------
    plan = create_documentation_plan(selected_model)

    print("\nDocumentation Plan:")
    for view in plan.views:
        print(f"- {view}")

    # -----------------------------
    # 4️⃣ Layout Check
    # -----------------------------
    max_components = kb.layout_rules.get("max_components_per_view", 10)
    components = selected_model.get_logical_components()

    if len(components) > max_components:
        print("\n[LAYOUT WARNING] Logical view exceeds max components per view.")
    else:
        print("\nLayout check passed.")

    # -----------------------------
    # 5️⃣ Diagram Quality Rules
    # -----------------------------
    diagram_quality_rules = getattr(kb, "diagram_quality_rules", {})

    generated_files = []

    # -----------------------------
    # 6️⃣ Generate Diagrams
    # -----------------------------
    for view in plan.views:

        diagram_type = kb.view_to_diagram_mapping.get(view)

        print(f"\n[DEBUG] View: {view}")
        print(f"[DEBUG] Diagram type from KB: {diagram_type}")

        output_file = BASE_DIR / "docs" / "generated" / "diagrams" / f"{diagram_type}.puml"

        # -------- COMPONENT --------
        if diagram_type == "component_diagram":
            generate_component_diagram(selected_model, output_file)
            generated_files.append(output_file)

        # -------- DEPLOYMENT --------
        elif diagram_type == "deployment_diagram":
            generate_deployment_diagram(selected_model, output_file)
            generated_files.append(output_file)

        # -------- CONTEXT --------
        elif diagram_type == "context_diagram":
            generate_context_diagram(selected_model, output_file)
            generated_files.append(output_file)

        # -------- SEQUENCE (SELF-EVOLVING) --------
        elif diagram_type == "sequence_diagram":

            sequence_rules = diagram_quality_rules.get("sequence_diagram", {})

            # 1️⃣ Generate initial diagram using KB rules
            generate_sequence_diagram(
                selected_model,
                output_file,
                rules=sequence_rules
            )

            # 2️⃣ Compile PNG
            compile_plantuml(output_file)
            png_path = output_file.with_suffix(".png")

            # 3️⃣ Vision Analysis (type-aware)
            feedback = analyze_diagram(str(png_path), diagram_type="sequence")
            vision_text = feedback["choices"][0]["message"]["content"]

            print("\nVision Feedback:\n", vision_text)

            # 4️⃣ Regenerate improved version
            regenerate_sequence_with_feedback(
                selected_model,
                vision_text,
                output_file
            )
            # 5️⃣ Ricompila PNG aggiornato
            compile_plantuml(output_file)
            generated_files.append(output_file)

        # -------- SECURITY --------
        elif diagram_type == "security_diagram":
            generate_security_diagram(selected_model, output_file)
            generated_files.append(output_file)

        else:
            print(f"[INFO] Diagram type '{diagram_type}' not yet implemented.")

    # -----------------------------
    # 7️⃣ Summary
    # -----------------------------
    print("\nGenerated artifacts:")
    for file in generated_files:
        print(f"- {file}")
