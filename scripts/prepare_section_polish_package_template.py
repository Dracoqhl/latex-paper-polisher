#!/usr/bin/env python3
import json
import sys
from pathlib import Path


SUPPORTED_ITEM_KINDS = {"paragraph": "p", "caption": "c"}


def find_summary_section(summary: dict, section_id: str) -> dict | None:
    for section in summary.get("section_map", []):
        if section.get("section_id") == section_id:
            return section
    return None


def find_inspection_section(inspection: dict, summary_section: dict) -> dict | None:
    source_file = summary_section.get("source_file")
    title = summary_section.get("title")
    for section in inspection.get("sections", []):
        if section.get("file") == source_file and section.get("title") == title:
            return section
    return None


def next_section_in_file(inspection: dict, current: dict) -> dict | None:
    candidates = [
        section
        for section in inspection.get("sections", [])
        if section.get("file") == current.get("file") and section.get("line", 0) > current.get("line", 0)
    ]
    return min(candidates, key=lambda section: section.get("line", 0), default=None)


def item_risks(source_item: dict) -> list[str]:
    risks = []
    if source_item.get("has_cjk_or_fullwidth"):
        risks.append("Contains CJK or full-width characters detected by inspection.")
    return risks


def build_item(section_id: str, source_item: dict, counts: dict[str, int]) -> dict:
    kind = source_item.get("kind", "paragraph")
    prefix = SUPPORTED_ITEM_KINDS.get(kind, "x")
    counts[prefix] = counts.get(prefix, 0) + 1
    original_text = source_item.get("text", "")
    return {
        "item_id": f"{section_id}-{prefix}{counts[prefix]:03d}",
        "item_type": kind,
        "source_file": source_item.get("file", ""),
        "line_range": [source_item.get("start_line"), source_item.get("end_line")],
        "original_text": original_text,
        "suggested_text": "",
        "revision_notes": [],
        "risks": item_risks(source_item),
        "questions": [],
        "editable_text": original_text,
    }


def section_items(inspection: dict, section_id: str, current_section: dict) -> list[dict]:
    source_file = current_section.get("file")
    start_line = current_section.get("line", 0)
    next_section = next_section_in_file(inspection, current_section)
    end_before = next_section.get("line", 10**12) if next_section else 10**12
    counts: dict[str, int] = {}
    items = []
    for source_item in inspection.get("paragraphs", []):
        if source_item.get("file") != source_file:
            continue
        if source_item.get("kind") not in SUPPORTED_ITEM_KINDS:
            continue
        start = source_item.get("start_line", 0)
        if start <= start_line or start >= end_before:
            continue
        items.append(build_item(section_id, source_item, counts))
    return items


def build_package(inspection: dict, summary: dict, summary_path: Path, section_id: str) -> tuple[dict | None, list[str]]:
    errors = []
    if summary.get("schema_version") != 1 or summary.get("mode") != "paper_summary":
        errors.append("paper summary must use schema_version 1 and mode paper_summary")
    if not str(summary.get("thesis", "")).strip():
        errors.append("paper summary thesis must not be empty")
    summary_section = find_summary_section(summary, section_id)
    if summary_section is None:
        errors.append(f"section_id not found in paper summary: {section_id}")
        return None, errors
    if not str(summary_section.get("role", "")).strip():
        errors.append(f"section_map entry missing role for section_id: {section_id}")
    inspection_section = find_inspection_section(inspection, summary_section)
    if inspection_section is None:
        errors.append(f"section not found in inspection: {section_id}")
        return None, errors
    if errors:
        return None, errors
    return {
        "schema_version": 1,
        "mode": "section_polish_package",
        "section_id": section_id,
        "section_title": summary_section.get("title", ""),
        "source_file": summary_section.get("source_file", ""),
        "paper_summary_ref": str(summary_path),
        "paper_context": {
            "thesis": summary.get("thesis", ""),
            "contributions": summary.get("contributions", []),
            "terminology": summary.get("terminology", []),
            "macro_risks": summary.get("macro_risks", []),
            "structural_suggestions": summary.get("structural_suggestions", []),
            "polishing_guidance": summary.get("polishing_guidance", []),
            "section_role": summary_section.get("role", ""),
        },
        "items": section_items(inspection, section_id, inspection_section),
    }, []


def run(inspection_path: Path, summary_path: Path, section_id: str, output_path: Path) -> dict:
    inspection = json.loads(inspection_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    package, errors = build_package(inspection, summary, summary_path, section_id)
    if errors or package is None:
        return {"ok": False, "section_id": section_id, "output": None, "errors": errors}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "section_id": section_id, "output": str(output_path), "item_count": len(package["items"]), "errors": []}


def main(argv: list[str]) -> int:
    if len(argv) != 5:
        print("usage: prepare_section_polish_package_template.py INSPECTION_JSON PAPER_SUMMARY_JSON SECTION_ID OUTPUT_JSON", file=sys.stderr)
        return 2
    result = run(Path(argv[1]), Path(argv[2]), argv[3], Path(argv[4]))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
