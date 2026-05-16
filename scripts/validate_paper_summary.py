#!/usr/bin/env python3
import json
import sys
from pathlib import Path


REQUIRED_FIELDS = {
    "schema_version",
    "mode",
    "project_root",
    "main_file",
    "thesis",
    "contributions",
    "section_map",
    "terminology",
    "macro_risks",
    "structural_suggestions",
    "polishing_guidance",
}

LIST_FIELDS = {
    "contributions",
    "section_map",
    "terminology",
    "macro_risks",
    "structural_suggestions",
    "polishing_guidance",
}

SECTION_FIELDS = {"section_id", "title", "source_file", "role"}


def validate(summary: dict) -> dict:
    errors = []
    for field in sorted(REQUIRED_FIELDS - summary.keys()):
        errors.append(f"missing required field: {field}")
    if summary.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if summary.get("mode") != "paper_summary":
        errors.append("mode must be paper_summary")
    if not str(summary.get("thesis", "")).strip():
        errors.append("thesis must not be empty")
    for field in sorted(LIST_FIELDS):
        if field in summary and not isinstance(summary[field], list):
            errors.append(f"{field} must be a list")
    section_map = summary.get("section_map")
    if isinstance(section_map, list):
        for index, section in enumerate(section_map):
            if not isinstance(section, dict):
                errors.append(f"section_map[{index}] must be an object")
                continue
            for field in sorted(SECTION_FIELDS - section.keys()):
                errors.append(f"section_map[{index}] missing required field: {field}")
    return {
        "ok": not errors,
        "project_root": summary.get("project_root"),
        "main_file": summary.get("main_file"),
        "section_count": len(section_map) if isinstance(section_map, list) else 0,
        "errors": errors,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_paper_summary.py PAPER_SUMMARY_JSON", file=sys.stderr)
        return 2
    summary = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    validation = validate(summary)
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
