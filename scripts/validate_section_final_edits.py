#!/usr/bin/env python3
import json
import sys
from pathlib import Path


EDIT_FIELDS = {
    "schema_version",
    "mode",
    "section_id",
    "section_title",
    "items",
}

ITEM_FIELDS = {
    "item_id",
    "source_file",
    "line_range",
    "original_text",
    "final_text",
}


def validate_item(package_item: dict, edit_item: dict, index: int) -> list[str]:
    errors = []
    for field in sorted(ITEM_FIELDS - edit_item.keys()):
        errors.append(f"items[{index}] missing required field: {field}")
    if edit_item.get("item_id") != package_item.get("item_id"):
        errors.append(f"items[{index}].item_id does not match section package")
    if edit_item.get("source_file") != package_item.get("source_file"):
        errors.append(f"items[{index}].source_file does not match section package")
    if edit_item.get("line_range") != package_item.get("line_range"):
        errors.append(f"items[{index}].line_range does not match section package")
    if edit_item.get("original_text") != package_item.get("original_text"):
        errors.append(f"items[{index}].original_text does not match section package")
    if not isinstance(edit_item.get("final_text"), str) or edit_item.get("final_text") == "":
        errors.append(f"items[{index}].final_text must not be empty")
    return errors


def validate(package: dict, edits: dict) -> dict:
    errors = []
    for field in sorted(EDIT_FIELDS - edits.keys()):
        errors.append(f"missing required field: {field}")
    if edits.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if edits.get("mode") != "section_final_edits":
        errors.append("mode must be section_final_edits")
    if edits.get("section_id") != package.get("section_id"):
        errors.append("section_id does not match section package")
    if edits.get("section_title") != package.get("section_title"):
        errors.append("section_title does not match section package")

    package_items = package.get("items", [])
    edit_items = edits.get("items")
    if not isinstance(edit_items, list):
        errors.append("items must be a list")
    elif len(edit_items) != len(package_items):
        errors.append("items must match section package item count")
    elif [item.get("item_id") for item in edit_items] != [item.get("item_id") for item in package_items]:
        errors.append("items must preserve section package item order")
    else:
        for index, (package_item, edit_item) in enumerate(zip(package_items, edit_items)):
            if not isinstance(edit_item, dict):
                errors.append(f"items[{index}] must be an object")
            else:
                errors.extend(validate_item(package_item, edit_item, index))

    return {
        "ok": not errors,
        "section_id": edits.get("section_id"),
        "item_count": len(edit_items) if isinstance(edit_items, list) else 0,
        "errors": errors,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: validate_section_final_edits.py SECTION_PACKAGE_JSON SECTION_FINAL_EDITS_JSON", file=sys.stderr)
        return 2
    package = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    edits = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    summary = validate(package, edits)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
