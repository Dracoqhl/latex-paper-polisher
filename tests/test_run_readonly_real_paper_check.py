import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PROJECT = ROOT / "fixtures" / "sample-paper"
SCRIPT = ROOT.parent / "scripts" / "run_readonly_real_paper_check.py"


def snapshot_mtimes(project: Path) -> dict[str, int]:
    return {
        str(path.relative_to(project)): path.stat().st_mtime_ns
        for path in project.rglob("*")
        if path.is_file()
    }


def test_readonly_check_writes_outputs_without_touching_project(tmp_path):
    before = snapshot_mtimes(PROJECT)
    output_dir = tmp_path / "latex-test"

    subprocess.run(["python", str(SCRIPT), str(PROJECT), str(output_dir)], check=True)

    after = snapshot_mtimes(PROJECT)
    assert after == before

    map_path = output_dir / "project-map.json"
    task_path = output_dir / "task-skeleton.json"
    summary_path = output_dir / "readonly-summary.json"
    assert map_path.exists()
    assert task_path.exists()
    assert summary_path.exists()

    project_map = json.loads(map_path.read_text(encoding="utf-8"))
    tasks = json.loads(task_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert project_map["main_file"] == "main.tex"
    assert tasks["requires_main_agent_review"] is True
    assert summary["project_unchanged"] is True
    assert summary["outputs"]["project_map"] == str(map_path)
