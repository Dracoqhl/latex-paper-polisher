#!/usr/bin/env python3
import json
import sys
from pathlib import Path

from validate_writeback import validate as validate_latex_constructs


def count_matches(text: str, needle: str) -> int:
    if needle == "":
        return 0
    count = 0
    start = 0
    while True:
        index = text.find(needle, start)
        if index == -1:
            return count
        count += 1
        start = index + len(needle)


def validate_candidate(candidate: dict) -> list[str]:
    errors = []
    if candidate.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if candidate.get("mode") != "section_writeback_candidate":
        errors.append("mode must be section_writeback_candidate")
    if candidate.get("source_write_permitted") is not False:
        errors.append("source_write_permitted must be false before preflight")
    if candidate.get("validation_required") is not True:
        errors.append("validation_required must be true")
    if not isinstance(candidate.get("items"), list) or not candidate.get("items"):
        errors.append("items must be a non-empty list")
    return errors


def preflight_item(project_root: Path, item: dict) -> tuple[dict, list[str]]:
    errors = []
    source_path = project_root / item["source_file"]
    if not source_path.exists():
        report = {
            "item_id": item.get("item_id"),
            "source_file": item.get("source_file"),
            "match_count": 0,
            "latex_validation": {"ok": False, "warnings": ["source file not found"]},
        }
        return report, [f"{item.get('item_id')} source file not found: {item.get('source_file')}"]

    source_text = source_path.read_text(encoding="utf-8")
    match_count = count_matches(source_text, item["original_text"])
    latex_validation = validate_latex_constructs(item["original_text"], item["final_text"])
    report = {
        "item_id": item["item_id"],
        "source_file": item["source_file"],
        "line_range": item.get("line_range"),
        "match_count": match_count,
        "latex_validation": latex_validation,
    }
    if match_count != 1:
        errors.append(f"{item['item_id']} original_text match count is {match_count}")
    for warning in latex_validation["warnings"]:
        errors.append(f"{item['item_id']}: {warning}")
    return report, errors


def run(project_root: Path, candidate_path: Path) -> dict:
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    errors = validate_candidate(candidate)
    item_reports = []
    if not errors:
        for item in candidate["items"]:
            report, item_errors = preflight_item(project_root, item)
            item_reports.append(report)
            errors.extend(item_errors)
    return {
        "ok": not errors,
        "mode": "section_writeback_preflight",
        "section_id": candidate.get("section_id"),
        "project_root": str(project_root),
        "source_write_permitted": False,
        "items": item_reports,
        "errors": errors,
    }


def main(argv: list[str]) -> int:
    if len(argv) not in {3, 4}:
        print("usage: preflight_section_writeback.py PROJECT_ROOT SECTION_WRITEBACK_CANDIDATE_JSON [OUTPUT_JSON]", file=sys.stderr)
        return 2
    try:
        summary = run(Path(argv[1]), Path(argv[2]))
    except FileNotFoundError as exc:
        print(f"input file not found: {exc.filename}", file=sys.stderr)
        return 1
    if len(argv) == 4:
        output_path = Path(argv[3])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
