#!/usr/bin/env python3
import json
import sys
from pathlib import Path

from validate_section_final_edits import validate


def ordered_unique(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def build_candidate(package: dict, edits: dict) -> dict:
    items = [
        {
            "item_id": item["item_id"],
            "source_file": item["source_file"],
            "line_range": item["line_range"],
            "original_text": item["original_text"],
            "final_text": item["final_text"],
        }
        for item in edits["items"]
    ]
    return {
        "schema_version": 1,
        "mode": "section_writeback_candidate",
        "section_id": edits["section_id"],
        "section_title": edits["section_title"],
        "source_file": package["source_file"],
        "source_files": ordered_unique([item["source_file"] for item in items]),
        "items": items,
        "validation_required": True,
        "source_write_permitted": False,
        "metadata": {
            "item_count": len(items),
            "paper_summary_ref": package.get("paper_summary_ref"),
        },
    }


def run(package_path: Path, edits_path: Path, output_path: Path) -> dict:
    package = json.loads(package_path.read_text(encoding="utf-8"))
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    summary = validate(package, edits)
    if not summary["ok"]:
        return summary

    candidate = build_candidate(package, edits)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "output": str(output_path),
        "section_id": candidate["section_id"],
        "item_count": len(candidate["items"]),
        "validation_required": True,
        "source_write_permitted": False,
        "errors": [],
    }


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(
            "usage: prepare_section_writeback_candidate.py SECTION_PACKAGE_JSON SECTION_FINAL_EDITS_JSON OUTPUT_JSON",
            file=sys.stderr,
        )
        return 2
    try:
        summary = run(Path(argv[1]), Path(argv[2]), Path(argv[3]))
    except FileNotFoundError as exc:
        print(f"input file not found: {exc.filename}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
