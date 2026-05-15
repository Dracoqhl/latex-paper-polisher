#!/usr/bin/env python3
import json
import sys
from pathlib import Path

from build_task_skeleton import build as build_task_skeleton
from inspect_latex_project import build_project_map


def snapshot_mtimes(project: Path) -> dict[str, int]:
    return {
        str(path.relative_to(project)): path.stat().st_mtime_ns
        for path in project.rglob("*")
        if path.is_file()
    }


def run(project: Path, output_dir: Path) -> dict:
    project = project.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    before = snapshot_mtimes(project)

    project_map = build_project_map(project)
    task_skeleton = build_task_skeleton(project_map)

    map_path = output_dir / "project-map.json"
    task_path = output_dir / "task-skeleton.json"
    summary_path = output_dir / "readonly-summary.json"
    map_path.write_text(json.dumps(project_map, ensure_ascii=False, indent=2), encoding="utf-8")
    task_path.write_text(json.dumps(task_skeleton, ensure_ascii=False, indent=2), encoding="utf-8")

    after = snapshot_mtimes(project)
    summary = {
        "project_root": str(project),
        "output_dir": str(output_dir),
        "project_unchanged": after == before,
        "outputs": {
            "project_map": str(map_path),
            "task_skeleton": str(task_path),
            "summary": str(summary_path),
        },
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: run_readonly_real_paper_check.py PROJECT_DIR OUTPUT_DIR", file=sys.stderr)
        return 2
    summary = run(Path(argv[1]), Path(argv[2]))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["project_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
