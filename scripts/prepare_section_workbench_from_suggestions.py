#!/usr/bin/env python3
import json
import sys
from pathlib import Path

import build_section_workbench
import merge_section_polish_suggestions


def run(package_path: Path, suggestions_path: Path, merged_package_path: Path, html_path: Path) -> dict:
    merge_summary = merge_section_polish_suggestions.run(package_path, suggestions_path, merged_package_path)
    if not merge_summary["ok"]:
        return {
            "ok": False,
            "section_id": merge_summary.get("section_id"),
            "merged_package": None,
            "html": None,
            "item_count": 0,
            "errors": merge_summary["errors"],
        }
    build_summary = build_section_workbench.run(merged_package_path, html_path)
    if not build_summary["ok"]:
        return {
            "ok": False,
            "section_id": merge_summary.get("section_id"),
            "merged_package": str(merged_package_path),
            "html": None,
            "item_count": merge_summary.get("item_count", 0),
            "errors": build_summary["errors"],
        }
    return {
        "ok": True,
        "section_id": build_summary["section_id"],
        "merged_package": str(merged_package_path),
        "html": str(html_path),
        "item_count": merge_summary["item_count"],
        "errors": [],
    }


def main(argv: list[str]) -> int:
    if len(argv) != 5:
        print(
            "usage: prepare_section_workbench_from_suggestions.py SECTION_PACKAGE_JSON SECTION_SUGGESTIONS_JSON OUTPUT_MERGED_PACKAGE_JSON OUTPUT_HTML",
            file=sys.stderr,
        )
        return 2
    summary = run(Path(argv[1]), Path(argv[2]), Path(argv[3]), Path(argv[4]))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
