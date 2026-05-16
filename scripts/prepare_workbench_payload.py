#!/usr/bin/env python3
import json
import sys
from pathlib import Path

from validate_specialist_suggestion import validate


def warning_items(suggestion: dict) -> list[str]:
    warnings: list[str] = []
    warnings.extend(f"Risk: {item}" for item in suggestion.get("risks", []))
    warnings.extend(f"Question: {item}" for item in suggestion.get("questions", []))
    return warnings


def build_payload(task_context: dict, suggestion: dict) -> dict:
    task = task_context["task"]
    target = suggestion["target"]
    return {
        "paragraph_id": suggestion["task_id"],
        "source_file": target["file"],
        "section": task["title"],
        "original_text": suggestion["original_text"],
        "suggested_text": suggestion["proposed_text"],
        "rationale": suggestion["rationale"],
        "warnings": warning_items(suggestion),
        "metadata": {
            "source": "specialist_suggestion",
            "task_type": task["type"],
            "assigned_role": task["assigned_role"],
            "line_range": target["line_range"],
        },
    }


def run(task_context_path: Path, suggestion_path: Path, output_path: Path) -> dict:
    task_context = json.loads(task_context_path.read_text(encoding="utf-8"))
    suggestion = json.loads(suggestion_path.read_text(encoding="utf-8"))
    validation = validate(task_context, suggestion)
    if not validation["ok"]:
        return validation

    payload = build_payload(task_context, suggestion)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "errors": [],
        "output": str(output_path),
    }


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: prepare_workbench_payload.py TASK_CONTEXT_JSON SUGGESTION_JSON OUTPUT_JSON", file=sys.stderr)
        return 2
    summary = run(Path(argv[1]), Path(argv[2]), Path(argv[3]))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
