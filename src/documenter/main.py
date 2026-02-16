from src.documenter.kb_updater import update_kb_from_feedback
from src.documenter.vision_rule_extractor import extract_rules_from_feedback
from src.documenter.vision_memory import save_vision_feedback
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
        return json.load(f)


def select_architecture(data: dict, architecture_id: str) -> dict:
    for arch in data.get("architectural_views", []):
        if arch["architecture_id"] == architecture_id:
            return arch
    raise ValueError(f"Architecture '{architecture_id}' not found.")


if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    # =============================
    # 1️⃣ Load Knowledge Base
    # =============================
    kb_path = BASE_DIR / "data" / "kb" / "documentation_rules.json"
    kb = load_knowledge_base(kb_path)

    print("\nKnowledge Base loaded.")
    print("View to diagram mapping:")
    for view, diagram in kb.view_to_diagram_mapping.items():
        print(f"- {view} -> {diagram}")

    # =============================
    # 2️⃣ Load Architecture
    # =============================
    input_path = BASE_DIR / "data" / "input" / "finalArchitecture.json"
    architecture_data = load_architecture(input_path)

    selected_id = "Microservices Architecture"
    selected_architecture = select_architecture(architecture_data, selected_id)
    selected_model = ArchitectureModel(selected_architecture)

    print(f"\nSelected architecture: {selected_model.id}")

    # =============================
    # 3️⃣ Documentation Plan
    # =============================
    plan = create_documentation_plan(selected_model)

    print("\nDocumentation Plan:")
    for view in plan.views:
        print(f"- {view}")

    # =============================
    # 4️⃣ Layout Check
    # =============================
    max_components = kb.layout_rules.get("max_components_per_view", 10)
    components = selected_model.get_logical_components()

    if len(components) > max_components:
        print("\n[LAYOUT WARNING] Logical view exceeds max components per view.")
    else:
        print("\nLayout check passed.")

    generated_files = []

    # =============================
    # 5️⃣ Generate Diagrams
    # =============================
    for view in plan.views:

        diagram_type = kb.view_to_diagram_mapping.get(view)

        print(f"\n[DEBUG] View: {view}")
        print(f"[DEBUG] Diagram type from KB: {diagram_type}")

        output_file = BASE_DIR / "docs" / "generated" / "diagrams" / f"{diagram_type}.puml"

        # ==========================================
        # SEQUENCE DIAGRAM (Self-Evolving)
        # ==========================================
        if diagram_type == "sequence_diagram":

            # 1️⃣ Generate base version
            generate_sequence_diagram(selected_model, output_file)

            # 2️⃣ Compile PNG
            compile_plantuml(output_file)
            png_path = output_file.with_suffix(".png")

            # 3️⃣ Analyze with Vision
            feedback = analyze_diagram(str(png_path), diagram_type="sequence")

            if isinstance(feedback, dict) and "choices" in feedback:

                vision_text = feedback["choices"][0]["message"]["content"]
                print("\nVision Feedback (sequence):\n", vision_text)

                # 4️⃣ Extract structured rules (LLM)
                new_rules = extract_rules_from_feedback(
                    diagram_type,
                    vision_text
                )

                # 5️⃣ Update KB dynamically
                if new_rules:
                    update_kb_from_feedback(
                        kb_path,
                        diagram_type,
                        new_rules
                    )
                    print(f"[KB UPDATE] Nuove regole salvate: {new_rules}")

                # 6️⃣ Regenerate improved version
                regenerate_sequence_with_feedback(
                    selected_model,
                    vision_text,
                    output_file
                )

                # 7️⃣ Recompile improved version
                compile_plantuml(output_file)

                # 8️⃣ Save memory
                save_vision_feedback(
                    BASE_DIR,
                    diagram_type,
                    selected_model.id,
                    vision_text
                )

            else:
                print("\n[VISION FALLBACK] Timeout o non disponibile. Attivazione rule-based fallback.")

                # Fallback simulato minimale
                simulated_feedback = "Enforce left to right order and avoid duplicates."

                new_rules = extract_rules_from_feedback(
                    diagram_type,
                    simulated_feedback
                )

                if new_rules:
                    update_kb_from_feedback(
                        kb_path,
                        diagram_type,
                        new_rules
                    )
                    print(f"[KB UPDATE - FALLBACK] Nuove regole salvate: {new_rules}")

        # ==========================================
        # OTHER DIAGRAMS (Deterministic)
        # ==========================================
        elif diagram_type == "component_diagram":
            generate_component_diagram(selected_model, output_file)

        elif diagram_type == "deployment_diagram":
            generate_deployment_diagram(selected_model, output_file)

        elif diagram_type == "context_diagram":
            generate_context_diagram(selected_model, output_file)

        elif diagram_type == "security_diagram":
            generate_security_diagram(selected_model, output_file)

        else:
            print(f"[INFO] Diagram type '{diagram_type}' not implemented.")

        generated_files.append(output_file)

    # =============================
    # 6️⃣ Summary
    # =============================
    print("\nGenerated artifacts:")
    for file in generated_files:
        print(f"- {file}")