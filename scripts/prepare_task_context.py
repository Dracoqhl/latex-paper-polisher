#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def find_task(task_board: dict, task_id: str) -> dict | None:
    for task in task_board.get("tasks", []):
        if task["id"] == task_id:
            return task
    return None


def read_source_context(project_root: Path, file_path: str) -> dict:
    path = project_root / file_path
    text = path.read_text(encoding="utf-8")
    return {
        "file": file_path,
        "line_start": 1,
        "line_end": len(text.splitlines()),
        "text": text,
    }


def build_context_package(task_board: dict, task: dict) -> dict:
    project_root = Path(task_board["project_root"])
    source_contexts = [
        read_source_context(project_root, file_path)
        for file_path in task.get("target_files", [])
    ]
    return {
        "schema_version": 1,
        "mode": "task_context_package",
        "project_root": task_board["project_root"],
        "main_file": task_board["main_file"],
        "task": task,
        "source_contexts": source_contexts,
        "instructions": [
            "Use this package for review or suggestion generation only.",
            "Do not edit source files from a specialist task.",
            "Preserve LaTeX commands, citations, labels, refs, math, comments, and environments.",
        ],
    }


def render_markdown(package: dict) -> str:
    task = package["task"]
    lines = [
        "# Task Context",
        "",
        f"Task: `{task['id']}`",
        f"Type: `{task['type']}`",
        f"Title: {task['title']}",
        f"Assigned role: `{task['assigned_role']}`",
        f"Status: `{task['status']}`",
        "",
        "## Acceptance Check",
        "",
        task["acceptance_check"],
        "",
        "## Source Context",
        "",
    ]
    for context in package["source_contexts"]:
        lines.extend([
            f"### `{context['file']}`",
            "",
            f"Lines: {context['line_start']}-{context['line_end']}",
            "",
            "```tex",
            context["text"],
            "```",
            "",
        ])
    lines.extend([
        "## Instructions",
        "",
    ])
    for instruction in package["instructions"]:
        lines.append(f"- {instruction}")
    lines.append("")
    return "\n".join(lines)


def run(task_board_path: Path, task_id: str, output_dir: Path) -> dict:
    task_board = json.loads(task_board_path.read_text(encoding="utf-8"))
    task = find_task(task_board, task_id)
    if task is None:
        raise KeyError(task_id)

    output_dir.mkdir(parents=True, exist_ok=True)
    package = build_context_package(task_board, task)
    json_path = output_dir / f"task-context-{task_id}.json"
    markdown_path = output_dir / f"task-context-{task_id}.md"
    json_path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path.write_text(render_markdown(package), encoding="utf-8")
    return {
        "task_id": task_id,
        "outputs": {
            "json": str(json_path),
            "markdown": str(markdown_path),
        },
    }


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: prepare_task_context.py TASK_BOARD_JSON TASK_ID OUTPUT_DIR", file=sys.stderr)
        return 2
    try:
        summary = run(Path(argv[1]), argv[2], Path(argv[3]))
    except KeyError:
        print(f"task not found: {argv[2]}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
