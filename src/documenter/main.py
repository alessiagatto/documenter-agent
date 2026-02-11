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

    available = list_available_architectures(architecture_data)

    print("Available architectures:")
    for arch in available:
        print(f"- {arch}")

    selected_id = "Microservices Architecture"

    # 🔹 Selezione architettura
    selected_architecture = select_architecture(architecture_data, selected_id)

    # 🔹 Creazione modello interno
    selected_model = ArchitectureModel(selected_architecture)

    print(f"\nSelected architecture: {selected_model.id}")
    print("Available views:")
    for view_name in selected_model.get_view_names():
        print(f"- {view_name}")
        print("\nLogical view components:")
components = selected_model.get_logical_components()

for comp in components:
    print(f"- {comp.id}")

