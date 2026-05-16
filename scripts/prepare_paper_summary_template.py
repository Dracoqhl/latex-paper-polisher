#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


DEFAULT_POLISHING_GUIDANCE = [
    "Preserve LaTeX citations, labels, refs, math, comments, and environments.",
    "Prefer precise academic English over stronger unsupported claims.",
]


def slugify_section_id(title: str, fallback: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or fallback


def build_section_map(project_map: dict) -> list[dict]:
    sections = []
    seen: set[str] = set()
    for index, section in enumerate(project_map.get("sections", []), start=1):
        title = section.get("title", "").strip()
        section_id = slugify_section_id(title, f"section-{index:03d}")
        if section_id in seen:
            section_id = f"{section_id}-{index:03d}"
        seen.add(section_id)
        sections.append(
            {
                "section_id": section_id,
                "title": title,
                "source_file": section.get("file", ""),
                "role": "",
            }
        )
    return sections


def prepare_template(project_map: dict) -> dict:
    return {
        "schema_version": 1,
        "mode": "paper_summary",
        "project_root": project_map.get("project_root", ""),
        "main_file": project_map.get("main_file", ""),
        "thesis": "",
        "contributions": [],
        "section_map": build_section_map(project_map),
        "terminology": [],
        "macro_risks": [],
        "structural_suggestions": [],
        "polishing_guidance": DEFAULT_POLISHING_GUIDANCE,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: prepare_paper_summary_template.py PROJECT_MAP_JSON OUTPUT_JSON", file=sys.stderr)
        return 2
    project_map_path = Path(argv[1])
    output_path = Path(argv[2])
    project_map = json.loads(project_map_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(prepare_template(project_map), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
