#!/usr/bin/env python3
"""Sanitize an n8n workflow export for public sharing.

Usage:
    python scripts/sanitize_n8n_export.py input.json output.json

This removes credential bindings and instance-specific workflow metadata.
It does not attempt to decide whether source URLs or workflow logic are
appropriate to publish; those still require human review.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


TOP_LEVEL_REMOVE = {
    "id",
    "versionId",
    "meta",
    "shared",
    "tags",
    "pinData",
}


def sanitize_node(node: dict) -> dict:
    node = dict(node)

    # Credential references may contain private account/instance identifiers.
    node.pop("credentials", None)
    node.pop("webhookId", None)

    # Execute Workflow references are instance-specific.
    if node.get("type") == "n8n-nodes-base.executeWorkflow":
        params = dict(node.get("parameters") or {})
        workflow_id = params.get("workflowId")

        if isinstance(workflow_id, dict):
            workflow_id = dict(workflow_id)
            workflow_id["value"] = ""
            workflow_id.pop("cachedResultUrl", None)
            params["workflowId"] = workflow_id
        elif workflow_id is not None:
            params["workflowId"] = ""

        node["parameters"] = params

    return node


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: sanitize_n8n_export.py INPUT.json OUTPUT.json"
        )

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    workflow = json.loads(input_path.read_text())

    for key in TOP_LEVEL_REMOVE:
        workflow.pop(key, None)

    workflow["nodes"] = [
        sanitize_node(node)
        for node in workflow.get("nodes", [])
    ]

    output_path.write_text(
        json.dumps(workflow, indent=2, ensure_ascii=False) + "\n"
    )

    print(f"Sanitized workflow written to: {output_path}")


if __name__ == "__main__":
    main()
