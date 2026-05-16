#!/usr/bin/env python3
import json
import sys
from pathlib import Path

from validate_section_polish_package import validate


def build_item_template(item: dict) -> dict:
    return {
        "item_id": item.get("item_id", ""),
        "source_file": item.get("source_file", ""),
        "line_range": item.get("line_range", []),
        "original_text": item.get("original_text", ""),
        "suggested_text": "",
        "revision_notes": [],
        "risks": [],
        "questions": [],
    }


def build_template(package: dict, package_path: Path) -> dict:
    return {
        "schema_version": 1,
        "mode": "section_polish_suggestions",
        "section_id": package.get("section_id", ""),
        "section_title": package.get("section_title", ""),
        "source_package_ref": str(package_path),
        "paper_context": package.get("paper_context", {}),
        "items": [build_item_template(item) for item in package.get("items", [])],
    }


def run(package_path: Path, output_path: Path) -> dict:
    package = json.loads(package_path.read_text(encoding="utf-8"))
    validation = validate(package)
    if not validation["ok"]:
        return {"ok": False, "section_id": package.get("section_id"), "output": None, "item_count": 0, "errors": validation["errors"]}
    template = build_template(package, package_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "section_id": template["section_id"], "output": str(output_path), "item_count": len(template["items"]), "errors": []}


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: prepare_section_polish_suggestions_template.py SECTION_PACKAGE_JSON OUTPUT_SUGGESTIONS_TEMPLATE_JSON", file=sys.stderr)
        return 2
    summary = run(Path(argv[1]), Path(argv[2]))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
