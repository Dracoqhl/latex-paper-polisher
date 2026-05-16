#!/usr/bin/env python3
import json
import sys
from pathlib import Path


SUGGESTION_FIELDS = {
    "schema_version",
    "mode",
    "section_id",
    "section_title",
    "source_package_ref",
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
}

LIST_FIELDS = {"revision_notes", "risks", "questions"}


def package_items_by_id(package: dict) -> dict:
    return {item.get("item_id"): item for item in package.get("items", []) if isinstance(item, dict)}


def validate_item(item: dict, index: int, source_items: dict) -> list[str]:
    errors = []
    for field in sorted(ITEM_FIELDS - item.keys()):
        errors.append(f"items[{index}] missing required field: {field}")
    source = source_items.get(item.get("item_id"))
    if source is None:
        errors.append(f"items[{index}].item_id not found in source package: {item.get('item_id')}")
        return errors
    for field in ("source_file", "line_range", "original_text"):
        if item.get(field) != source.get(field):
            errors.append(f"items[{index}].{field} does not match source package")
    if not str(item.get("suggested_text", "")).strip():
        errors.append(f"items[{index}].suggested_text must not be empty")
    for field in LIST_FIELDS:
        if field in item and not isinstance(item[field], list):
            errors.append(f"items[{index}].{field} must be a list")
    return errors


def validate(package: dict, suggestions: dict) -> dict:
    errors = []
    for field in sorted(SUGGESTION_FIELDS - suggestions.keys()):
        errors.append(f"missing required field: {field}")
    if suggestions.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if suggestions.get("mode") != "section_polish_suggestions":
        errors.append("mode must be section_polish_suggestions")
    if suggestions.get("section_id") != package.get("section_id"):
        errors.append("section_id does not match source package")
    if suggestions.get("section_title") != package.get("section_title"):
        errors.append("section_title does not match source package")
    items = suggestions.get("items")
    source_items = package_items_by_id(package)
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty list")
    elif isinstance(items, list):
        seen = set()
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"items[{index}] must be an object")
                continue
            item_id = item.get("item_id")
            if item_id in seen:
                errors.append(f"items[{index}].item_id is duplicated: {item_id}")
            seen.add(item_id)
            errors.extend(validate_item(item, index, source_items))
    return {
        "ok": not errors,
        "section_id": suggestions.get("section_id"),
        "item_count": len(items) if isinstance(items, list) else 0,
        "errors": errors,
    }


def load_and_validate(package_path: Path, suggestions_path: Path) -> tuple[dict, dict, dict]:
    package = json.loads(package_path.read_text(encoding="utf-8"))
    suggestions = json.loads(suggestions_path.read_text(encoding="utf-8"))
    return package, suggestions, validate(package, suggestions)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: validate_section_polish_suggestions.py SECTION_PACKAGE_JSON SECTION_SUGGESTIONS_JSON", file=sys.stderr)
        return 2
    _, _, summary = load_and_validate(Path(argv[1]), Path(argv[2]))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
