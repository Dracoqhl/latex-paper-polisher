import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
MAPPER = ROOT.parent / "scripts" / "inspect_latex_project.py"
SCRIPT = ROOT.parent / "scripts" / "build_task_skeleton.py"
PROJECT = ROOT / "fixtures" / "sample-paper"


def test_builds_section_oriented_task_skeleton(tmp_path):
    map_path = tmp_path / "project-map.json"
    task_path = tmp_path / "tasks.json"
    mapped = subprocess.run(
        ["python", str(MAPPER), "--map", str(PROJECT)],
        check=True,
        text=True,
        capture_output=True,
    )
    map_path.write_text(mapped.stdout, encoding="utf-8")

    subprocess.run(["python", str(SCRIPT), str(map_path), str(task_path)], check=True)

    data = json.loads(task_path.read_text(encoding="utf-8"))
    task_types = [task["type"] for task in data["tasks"]]
    assert data["schema_version"] == 1
    assert "macro_review" in task_types
    assert "section_polish" in task_types
    assert "caption_polish" in task_types
    assert "cjk_fullwidth_scan" in task_types
    assert all(task["status"] == "pending" for task in data["tasks"])


def test_task_skeleton_is_mechanical_not_final_agent_plan(tmp_path):
    map_path = tmp_path / "project-map.json"
    task_path = tmp_path / "tasks.json"
    mapped = subprocess.run(
        ["python", str(MAPPER), "--map", str(PROJECT)],
        check=True,
        text=True,
        capture_output=True,
    )
    map_path.write_text(mapped.stdout, encoding="utf-8")

    subprocess.run(["python", str(SCRIPT), str(map_path), str(task_path)], check=True)

    data = json.loads(task_path.read_text(encoding="utf-8"))
    assert data["mode"] == "mechanical_task_skeleton"
    assert data["requires_main_agent_review"] is True
