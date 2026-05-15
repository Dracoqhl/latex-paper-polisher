#!/usr/bin/env python3
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from build_task_skeleton import build as build_task_skeleton
from inspect_latex_project import build_project_map
from run_readonly_real_paper_check import snapshot_mtimes


GLOBAL_TASK_TYPES = {"macro_review", "terminology_check", "cjk_fullwidth_scan", "latex_safety_check"}


def task_phase(task: dict) -> str:
    if task["type"] in GLOBAL_TASK_TYPES:
        return "global"
    if task["type"] == "caption_polish":
        return "caption"
    return "section"


def build_task_board(task_skeleton: dict) -> dict:
    tasks = []
    for task in task_skeleton["tasks"]:
        board_task = dict(task)
        board_task.update({
            "priority": "normal",
            "phase": task_phase(task),
            "review_decision": "unreviewed",
            "user_notes": [],
            "main_agent_notes": [],
        })
        tasks.append(board_task)
    return {
        "schema_version": 1,
        "mode": "main_agent_review_board",
        "requires_user_review": True,
        "project_root": task_skeleton["project_root"],
        "main_file": task_skeleton["main_file"],
        "tasks": tasks,
    }


def render_task_review(task_board: dict) -> str:
    tasks = task_board["tasks"]
    type_counts = Counter(task["type"] for task in tasks)
    phase_groups: dict[str, list[dict]] = defaultdict(list)
    for task in tasks:
        phase_groups[task["phase"]].append(task)

    lines = [
        "# Task Review",
        "",
        f"Project: `{task_board['project_root']}`",
        f"Main file: `{task_board['main_file']}`",
        f"Total tasks: {len(tasks)}",
        "",
        "## Task Counts",
        "",
    ]
    for task_type, count in sorted(type_counts.items()):
        lines.append(f"- `{task_type}`: {count}")

    lines.extend([
        "",
        "## Recommended Review Order",
        "",
        "1. `macro_review`",
        "2. Abstract, Introduction, and Conclusion section tasks",
        "3. Main body section tasks",
        "4. `caption_polish` tasks",
        "5. Appendix section tasks",
        "6. `terminology_check`, `cjk_fullwidth_scan`, and `latex_safety_check`",
        "",
        "## Global Tasks",
        "",
    ])
    for task in phase_groups.get("global", []):
        lines.append(f"- `{task['type']}` `{task['id']}`: {task['title']}")

    lines.extend(["", "## Section Tasks", ""])
    for task in phase_groups.get("section", []):
        target = ", ".join(f"`{path}`" for path in task["target_files"])
        appendix_marker = " _(appendix)_" if any("appendix" in path.lower() or "9_appendix" in path for path in task["target_files"]) else ""
        lines.append(f"- `{task['id']}`: {task['title']} ({target}){appendix_marker}")

    lines.extend(["", "## Caption Tasks", ""])
    for task in phase_groups.get("caption", []):
        target = ", ".join(f"`{path}`" for path in task["target_files"])
        appendix_marker = " _(appendix)_" if any("appendix" in path.lower() or "9_appendix" in path for path in task["target_files"]) else ""
        lines.append(f"- `{task['id']}`: {task['title']} ({target}){appendix_marker}")

    lines.extend([
        "",
        "## Review Decisions",
        "",
        "Use `task-board.json` to mark tasks as `keep`, `skip`, `merge`, or `prioritize` in `review_decision`.",
        "Do not edit the source paper during task review.",
        "",
    ])
    return "\n".join(lines)


def run(project: Path, output_dir: Path) -> dict:
    project = project.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    before = snapshot_mtimes(project)

    project_map = build_project_map(project)
    task_skeleton = build_task_skeleton(project_map)
    task_board = build_task_board(task_skeleton)

    map_path = output_dir / "project-map.json"
    skeleton_path = output_dir / "task-skeleton.json"
    board_path = output_dir / "task-board.json"
    review_path = output_dir / "task-review.md"
    summary_path = output_dir / "readonly-summary.json"

    map_path.write_text(json.dumps(project_map, ensure_ascii=False, indent=2), encoding="utf-8")
    skeleton_path.write_text(json.dumps(task_skeleton, ensure_ascii=False, indent=2), encoding="utf-8")
    board_path.write_text(json.dumps(task_board, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.write_text(render_task_review(task_board), encoding="utf-8")

    after = snapshot_mtimes(project)
    summary = {
        "project_root": str(project),
        "output_dir": str(output_dir),
        "project_unchanged": after == before,
        "outputs": {
            "project_map": str(map_path),
            "task_skeleton": str(skeleton_path),
            "task_board": str(board_path),
            "task_review": str(review_path),
            "summary": str(summary_path),
        },
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main(argv: list[str]) -> int:
    if len(argv) not in {2, 3}:
        print("usage: prepare_review_bundle.py PROJECT_DIR [OUTPUT_DIR]", file=sys.stderr)
        return 2
    output_dir = Path(argv[2]) if len(argv) == 3 else Path("/data/latex_test")
    summary = run(Path(argv[1]), output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["project_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
