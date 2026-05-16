#!/usr/bin/env python3
import json
import sys
from pathlib import Path


REQUIRED_FIELDS = {
    "schema_version",
    "mode",
    "task_id",
    "target",
    "original_text",
    "proposed_text",
    "rationale",
    "latex_constructs_preserved",
    "risks",
    "questions",
}


def source_context_by_file(task_context: dict) -> dict[str, dict]:
    return {
        context["file"]: context
        for context in task_context.get("source_contexts", [])
    }


def validate(task_context: dict, suggestion: dict) -> dict:
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - suggestion.keys())
    for field in missing:
        errors.append(f"missing required field: {field}")

    if suggestion.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if suggestion.get("mode") != "specialist_suggestion":
        errors.append("mode must be specialist_suggestion")
    if suggestion.get("task_id") != task_context.get("task", {}).get("id"):
        errors.append("task_id does not match task context")

    target = suggestion.get("target")
    contexts_by_file = source_context_by_file(task_context)
    if not isinstance(target, dict):
        errors.append("target must be an object")
    else:
        target_file = target.get("file")
        target_range = target.get("line_range")
        context = contexts_by_file.get(target_file)
        if context is None:
            errors.append("target file is not part of task context")
        elif target_range != [context["line_start"], context["line_end"]]:
            errors.append("target line_range does not match task context")

    for field in ("rationale", "latex_constructs_preserved", "risks", "questions"):
        if field in suggestion and not isinstance(suggestion[field], list):
            errors.append(f"{field} must be a list")

    if "proposed_text" in suggestion and not isinstance(suggestion["proposed_text"], str):
        errors.append("proposed_text must be a string")
    elif suggestion.get("proposed_text", "") == "":
        errors.append("proposed_text must not be empty")

    if "original_text" in suggestion and not isinstance(suggestion["original_text"], str):
        errors.append("original_text must be a string")
    elif isinstance(target, dict):
        context = contexts_by_file.get(target.get("file"))
        if context is not None and suggestion.get("original_text") != context["text"]:
            errors.append("original_text does not match task context")

    return {
        "ok": not errors,
        "errors": errors,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: validate_specialist_suggestion.py TASK_CONTEXT_JSON SUGGESTION_JSON", file=sys.stderr)
        return 2
    task_context = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    suggestion = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    summary = validate(task_context, suggestion)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
