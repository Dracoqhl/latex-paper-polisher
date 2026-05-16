#!/usr/bin/env python3
import json
import sys
from pathlib import Path

from validate_section_polish_suggestions import load_and_validate


MERGED_FIELDS = ("suggested_text", "revision_notes", "risks", "questions")


def merge(package: dict, suggestions: dict, suggestions_path: Path) -> dict:
    suggestion_by_id = {item["item_id"]: item for item in suggestions["items"]}
    merged = json.loads(json.dumps(package, ensure_ascii=False))
    for item in merged.get("items", []):
        suggestion = suggestion_by_id.get(item.get("item_id"))
        if suggestion is None:
            continue
        for field in MERGED_FIELDS:
            item[field] = suggestion[field]
        item["editable_text"] = item["original_text"]
    metadata = merged.setdefault("metadata", {})
    metadata["suggestions_ref"] = str(suggestions_path)
    return merged


def run(package_path: Path, suggestions_path: Path, output_path: Path) -> dict:
    package, suggestions, validation = load_and_validate(package_path, suggestions_path)
    if not validation["ok"]:
        return {"ok": False, "output": None, "section_id": suggestions.get("section_id"), "errors": validation["errors"]}
    merged = merge(package, suggestions, suggestions_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "output": str(output_path), "section_id": merged.get("section_id"), "item_count": len(suggestions["items"]), "errors": []}


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: merge_section_polish_suggestions.py SECTION_PACKAGE_JSON SECTION_SUGGESTIONS_JSON OUTPUT_SECTION_PACKAGE_JSON", file=sys.stderr)
        return 2
    summary = run(Path(argv[1]), Path(argv[2]), Path(argv[3]))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
