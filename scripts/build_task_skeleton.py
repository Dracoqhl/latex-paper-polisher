#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return value or "untitled"


def make_task(
    task_id: str,
    task_type: str,
    title: str,
    target_files: list[str],
    anchors: list[dict],
    assigned_role: str,
    acceptance_check: str,
) -> dict:
    return {
        "id": task_id,
        "type": task_type,
        "title": title,
        "target_files": target_files,
        "anchors": anchors,
        "status": "pending",
        "assigned_role": assigned_role,
        "required_context": ["paper thesis", "section role", "terminology", "latex preservation rules"],
        "acceptance_check": acceptance_check,
    }


def build(project_map: dict) -> dict:
    tasks = [
        make_task(
            "macro-review",
            "macro_review",
            "Paper-level reviewer diagnosis",
            project_map["files"],
            [],
            "macro_reviewer",
            "User confirms the macro optimization direction before polishing begins.",
        ),
        make_task(
            "terminology-check",
            "terminology_check",
            "Terminology consistency pass",
            project_map["files"],
            [],
            "terminology_checker",
            "Main agent records stable terminology decisions in references/knowledge.md.",
        ),
        make_task(
            "cjk-fullwidth-scan",
            "cjk_fullwidth_scan",
            "Chinese and full-width punctuation scan",
            project_map["files"],
            [],
            "latex_safety_checker",
            "All flagged characters are reviewed before any source writeback.",
        ),
        make_task(
            "latex-safety-check",
            "latex_safety_check",
            "LaTeX safety review",
            project_map["files"],
            [],
            "latex_safety_checker",
            "No specialist output is accepted if it damages LaTeX constructs.",
        ),
    ]

    for section in project_map.get("sections", []):
        title = section["title"]
        tasks.append(make_task(
            f"{slug(title)}-section-polish",
            "section_polish",
            f"Polish {title}",
            [section["file"]],
            [section["anchor"]],
            "section_polisher",
            "User approves final section wording and validator reports no LaTeX construct damage.",
        ))

    for index, caption in enumerate(project_map.get("captions", []), start=1):
        label = caption.get("label") or f"caption-{index}"
        tasks.append(make_task(
            f"{slug(label)}-caption-polish",
            "caption_polish",
            f"Polish caption {label}",
            [caption["file"]],
            [caption["anchor"]],
            "caption_polisher",
            "Caption remains semantically consistent with surrounding text and preserved labels.",
        ))

    return {
        "schema_version": 1,
        "mode": "mechanical_task_skeleton",
        "requires_main_agent_review": True,
        "project_root": project_map["project_root"],
        "main_file": project_map["main_file"],
        "tasks": tasks,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: build_task_skeleton.py PROJECT_MAP_JSON OUTPUT_JSON", file=sys.stderr)
        return 2
    project_map = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    Path(argv[2]).write_text(json.dumps(build(project_map), ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
