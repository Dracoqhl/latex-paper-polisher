#!/usr/bin/env python3
import difflib
import json
import sys
from pathlib import Path

from preflight_section_writeback import run as run_preflight


def apply_items_to_text(source_text: str, items: list[dict]) -> str:
    updated = source_text
    for item in items:
        updated = updated.replace(item["original_text"], item["final_text"], 1)
    return updated


def unified_diff(source_file: str, before: str, after: str) -> str:
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"a/{source_file}",
            tofile=f"b/{source_file}",
        )
    )


def build_dry_run_report(project_root: Path, candidate: dict) -> dict:
    files = []
    for source_file in candidate["source_files"]:
        source_path = project_root / source_file
        before = source_path.read_text(encoding="utf-8")
        file_items = [item for item in candidate["items"] if item["source_file"] == source_file]
        after = apply_items_to_text(before, file_items)
        files.append(
            {
                "source_file": source_file,
                "item_count": len(file_items),
                "changed": before != after,
                "unified_diff": unified_diff(source_file, before, after),
            }
        )
    return {
        "ok": True,
        "mode": "section_writeback_apply_dry_run",
        "section_id": candidate["section_id"],
        "dry_run": True,
        "source_write_permitted": False,
        "files": files,
        "errors": [],
    }


def run(project_root: Path, candidate_path: Path, output_path: Path) -> dict:
    preflight = run_preflight(project_root, candidate_path)
    if not preflight["ok"]:
        return preflight
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    report = build_dry_run_report(project_root, candidate)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main(argv: list[str]) -> int:
    if len(argv) != 5 or argv[1] != "--dry-run":
        print("usage: apply_section_writeback_candidate.py --dry-run PROJECT_ROOT SECTION_WRITEBACK_CANDIDATE_JSON OUTPUT_JSON", file=sys.stderr)
        return 2
    try:
        summary = run(Path(argv[2]), Path(argv[3]), Path(argv[4]))
    except FileNotFoundError as exc:
        print(f"input file not found: {exc.filename}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
