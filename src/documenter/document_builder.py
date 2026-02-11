import json
from pathlib import Path
from src.documenter.models import ArchitectureModel
from src.documenter.planner import DocumentationPlan


def build_document_bundle(
    model: ArchitectureModel,
    plan: DocumentationPlan,
    generated_files: list,
    output_path: Path
):
    document = {
        "architecture_id": model.id,
        "architecture_name": model.name,
        "documented_views": plan.views,
        "components": [c.id for c in model.get_logical_components()],
        "relationships": [
            {
                "source": conn.source,
                "target": conn.target,
                "type": conn.type
            }
            for conn in model.get_logical_connectors()
        ],
        "generated_artifacts": [str(f) for f in generated_files]
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(document, f, indent=4)

    return document