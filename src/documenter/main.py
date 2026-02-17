from pathlib import Path
import json

from src.documenter.kb_loader import load_knowledge_base
from src.documenter.planner import create_documentation_plan
from src.documenter.models import ArchitectureModel

from src.documenter.uml_generator import (
    generate_security_diagram,
    generate_sequence_diagram,
    generate_context_diagram,
    generate_deployment_diagram,
    generate_component_diagram,
    regenerate_sequence_with_feedback,
    compile_plantuml,
)

from src.documenter.vision_analyzer import analyze_diagram
from src.documenter.vision_memory import save_vision_feedback
from src.documenter.document_builder import build_document_bundle


def load_architecture(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def select_architecture(data: dict, architecture_id: str) -> dict:
    for arch in data.get("architectural_views", []):
        if arch.get("architecture_id") == architecture_id:
            return arch
    raise ValueError(f"Architecture '{architecture_id}' not found.")


def safe_compile(puml_path: Path) -> bool:
    """Compila .puml -> .png. Ritorna True se esiste il PNG."""
    try:
        compile_plantuml(puml_path)
        return puml_path.with_suffix(".png").exists()
    except Exception as e:
        print(f"[WARNING] Compile failed for {puml_path.name}: {e}")
        return False


if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    # 1) KB
    kb_path = BASE_DIR / "data" / "kb" / "documentation_rules.json"
    kb = load_knowledge_base(kb_path)

    print("\nKnowledge Base loaded.")
    for view, diagram in kb.view_to_diagram_mapping.items():
        print(f"- {view} -> {diagram}")

    # 2) Architecture
    input_path = BASE_DIR / "data" / "input" / "finalArchitecture.json"
    architecture_data = load_architecture(input_path)

    selected_id = "Microservices Architecture"
    selected_architecture = select_architecture(architecture_data, selected_id)
    selected_model = ArchitectureModel(selected_architecture)

    print(f"\nSelected architecture: {selected_model.id}")

    # 3) Plan
    plan = create_documentation_plan(selected_model)
    print("\nDocumentation Plan:")
    for view in plan.views:
        print(f"- {view}")

    # 4) Layout check
    max_components = kb.layout_rules.get("max_components_per_view", 10)
    components = selected_model.get_logical_components()
    if len(components) > max_components:
        print("\n[LAYOUT WARNING] Logical view exceeds max components per view.")
    else:
        print("\nLayout check passed.")

    # Output dirs
    diagrams_dir = BASE_DIR / "docs" / "generated" / "diagrams"
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []

    # 5) Generate diagrams (+ compile PNG SEMPRE)
    for view in plan.views:
        diagram_type = kb.view_to_diagram_mapping.get(view)
        print(f"\n[DEBUG] View: {view}")
        print(f"[DEBUG] Diagram type from KB: {diagram_type}")

        puml_path = diagrams_dir / f"{diagram_type}.puml"

        if diagram_type == "component_diagram":
            generate_component_diagram(selected_model, puml_path)
            safe_compile(puml_path)

        elif diagram_type == "deployment_diagram":
            generate_deployment_diagram(selected_model, puml_path)
            safe_compile(puml_path)

        elif diagram_type == "context_diagram":
            generate_context_diagram(selected_model, puml_path)
            safe_compile(puml_path)

        elif diagram_type == "security_diagram":
            generate_security_diagram(selected_model, puml_path)
            safe_compile(puml_path)

        elif diagram_type == "sequence_diagram":
            # Base
            generate_sequence_diagram(selected_model, puml_path)
            png_ok = safe_compile(puml_path)

            # Vision (se png ok)
            if png_ok:
                png_path = puml_path.with_suffix(".png")
                feedback = analyze_diagram(str(png_path), diagram_type="sequence")

                if isinstance(feedback, dict) and "choices" in feedback:
                    vision_text = feedback["choices"][0]["message"]["content"]
                    print("\nVision Feedback (sequence):\n", vision_text)

                    regenerate_sequence_with_feedback(selected_model, vision_text, puml_path)
                    safe_compile(puml_path)

                    save_vision_feedback(BASE_DIR, diagram_type, selected_model.id, vision_text)
                else:
                    print("\n[VISION] Timeout o non disponibile (ok: fallback deterministico).")
            else:
                print("\n[SEQUENCE] PNG non generato, salto analisi Vision.")

        else:
            print(f"[INFO] Diagram type '{diagram_type}' not implemented.")

        generated_files.append(puml_path)

    # 6) Build doc (md+pdf) DOPO che i png sono pronti
    build_document_bundle(BASE_DIR, plan, selected_model, kb)

    print("\nGenerated artifacts:")
    for f in generated_files:
        print(f"- {f}")