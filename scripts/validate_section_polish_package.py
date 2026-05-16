#!/usr/bin/env python3
import json
import sys
from pathlib import Path


PACKAGE_FIELDS = {
    "schema_version",
    "mode",
    "section_id",
    "section_title",
    "source_file",
    "paper_summary_ref",
    "items",
}

ITEM_FIELDS = {
    "item_id",
    "source_file",
    "line_range",
    "original_text",
    "suggested_text",
    "revision_notes",
    "risks",
    "questions",
    "editable_text",
}


def validate_item(item: dict, index: int) -> list[str]:
    errors = []
    for field in sorted(ITEM_FIELDS - item.keys()):
        errors.append(f"items[{index}] missing required field: {field}")
    if item.get("editable_text") != item.get("original_text"):
        errors.append(f"items[{index}].editable_text must equal original_text by default")
    for field in ("revision_notes", "risks", "questions"):
        if field in item and not isinstance(item[field], list):
            errors.append(f"items[{index}].{field} must be a list")
    line_range = item.get("line_range")
    if line_range is not None and (
        not isinstance(line_range, list)
        or len(line_range) != 2
        or not all(isinstance(value, int) for value in line_range)
    ):
        errors.append(f"items[{index}].line_range must be a two-integer list")
    return errors


def validate(package: dict) -> dict:
    errors = []
    for field in sorted(PACKAGE_FIELDS - package.keys()):
        errors.append(f"missing required field: {field}")
    if package.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if package.get("mode") != "section_polish_package":
        errors.append("mode must be section_polish_package")
    items = package.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty list")
    elif isinstance(items, list):
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"items[{index}] must be an object")
            else:
                errors.extend(validate_item(item, index))
    return {
        "ok": not errors,
        "section_id": package.get("section_id"),
        "item_count": len(items) if isinstance(items, list) else 0,
        "errors": errors,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_section_polish_package.py SECTION_PACKAGE_JSON", file=sys.stderr)
        return 2
    package = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    summary = validate(package)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
