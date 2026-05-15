import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PROJECT = ROOT / "fixtures" / "sample-paper"
SCRIPT = ROOT.parent / "scripts" / "prepare_review_bundle.py"


def snapshot_mtimes(project: Path) -> dict[str, int]:
    return {
        str(path.relative_to(project)): path.stat().st_mtime_ns
        for path in project.rglob("*")
        if path.is_file()
    }


def test_prepare_review_bundle_writes_board_and_review_without_touching_project(tmp_path):
    before = snapshot_mtimes(PROJECT)
    output_dir = tmp_path / "latex-test"

    subprocess.run(["python", str(SCRIPT), str(PROJECT), str(output_dir)], check=True)

    after = snapshot_mtimes(PROJECT)
    assert after == before

    board_path = output_dir / "task-board.json"
    review_path = output_dir / "task-review.md"
    summary_path = output_dir / "readonly-summary.json"
    assert board_path.exists()
    assert review_path.exists()
    assert summary_path.exists()

    board = json.loads(board_path.read_text(encoding="utf-8"))
    review = review_path.read_text(encoding="utf-8")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert board["mode"] == "main_agent_review_board"
    assert board["requires_user_review"] is True
    assert len(board["tasks"]) >= 6
    assert all("review_decision" in task for task in board["tasks"])
    assert all("user_notes" in task for task in board["tasks"])
    assert "## Recommended Review Order" in review
    assert "macro_review" in review
    assert "section_polish" in review
    assert summary["project_unchanged"] is True
    assert summary["outputs"]["task_board"] == str(board_path)


def test_task_board_preserves_skeleton_tasks_and_adds_review_fields(tmp_path):
    output_dir = tmp_path / "latex-test"
    subprocess.run(["python", str(SCRIPT), str(PROJECT), str(output_dir)], check=True)

    skeleton = json.loads((output_dir / "task-skeleton.json").read_text(encoding="utf-8"))
    board = json.loads((output_dir / "task-board.json").read_text(encoding="utf-8"))

    skeleton_ids = [task["id"] for task in skeleton["tasks"]]
    board_ids = [task["id"] for task in board["tasks"]]
    assert board_ids == skeleton_ids
    assert board["project_root"] == skeleton["project_root"]
    assert board["main_file"] == skeleton["main_file"]
    for task in board["tasks"]:
        assert task["priority"] == "normal"
        assert task["phase"] in {"global", "section", "caption"}
        assert task["review_decision"] == "unreviewed"
        assert task["main_agent_notes"] == []
