#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def first_target_context(task_context: dict) -> dict:
    source_contexts = task_context.get("source_contexts", [])
    if not source_contexts:
        raise ValueError("task context has no source contexts")
    return source_contexts[0]


def build_template(task_context: dict) -> dict:
    task = task_context["task"]
    context = first_target_context(task_context)
    return {
        "schema_version": 1,
        "mode": "specialist_suggestion",
        "task_id": task["id"],
        "target": {
            "file": context["file"],
            "line_range": [context["line_start"], context["line_end"]],
        },
        "original_text": context["text"],
        "proposed_text": "",
        "rationale": [],
        "latex_constructs_preserved": [],
        "risks": [],
        "questions": [],
        "metadata": {
            "assigned_role": task["assigned_role"],
            "suggestion_only": True,
            "source_context_mode": task_context["mode"],
        },
    }


def run(task_context_path: Path, output_path: Path) -> dict:
    task_context = json.loads(task_context_path.read_text(encoding="utf-8"))
    template = build_template(task_context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "task_id": template["task_id"],
        "output": str(output_path),
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: prepare_suggestion_template.py TASK_CONTEXT_JSON OUTPUT_JSON", file=sys.stderr)
        return 2
    try:
        summary = run(Path(argv[1]), Path(argv[2]))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
