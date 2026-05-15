import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).parent
PROJECT = Path("/data/proj/icml2026/ICML2026")
MAPPER = ROOT.parent / "scripts" / "inspect_latex_project.py"
TASKER = ROOT.parent / "scripts" / "build_task_skeleton.py"


pytestmark = pytest.mark.skipif(not PROJECT.exists(), reason="real ICML paper fixture is not available")


def snapshot_mtimes(project: Path) -> dict[str, int]:
    return {
        str(path.relative_to(project)): path.stat().st_mtime_ns
        for path in project.rglob("*")
        if path.is_file()
    }


def test_real_icml_project_mapping_is_read_only(tmp_path):
    before = snapshot_mtimes(PROJECT)
    map_path = tmp_path / "icml-project-map.json"
    task_path = tmp_path / "icml-task-skeleton.json"

    mapped = subprocess.run(
        ["python", str(MAPPER), "--map", str(PROJECT)],
        check=True,
        text=True,
        capture_output=True,
    )
    map_path.write_text(mapped.stdout, encoding="utf-8")
    subprocess.run(["python", str(TASKER), str(map_path), str(task_path)], check=True)

    after = snapshot_mtimes(PROJECT)
    assert after == before

    project_map = json.loads(map_path.read_text(encoding="utf-8"))
    tasks = json.loads(task_path.read_text(encoding="utf-8"))
    assert project_map["main_file"] == "example_paper.tex"
    assert "src/1_introduction.tex" in project_map["files"]
    assert any(section["title"] == "Introduction" for section in project_map["sections"])
    assert any(task["type"] == "section_polish" and "Introduction" in task["title"] for task in tasks["tasks"])
    assert tasks["requires_main_agent_review"] is True
