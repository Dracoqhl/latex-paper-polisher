import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PROJECT = ROOT / "fixtures" / "sample-paper"
REVIEW_BUNDLE = ROOT.parent / "scripts" / "prepare_review_bundle.py"
SCRIPT = ROOT.parent / "scripts" / "prepare_task_context.py"


def test_prepare_task_context_writes_json_and_markdown(tmp_path):
    bundle_dir = tmp_path / "bundle"
    context_dir = tmp_path / "context"
    subprocess.run(["python", str(REVIEW_BUNDLE), str(PROJECT), str(bundle_dir)], check=True)

    subprocess.run(
        [
            "python",
            str(SCRIPT),
            str(bundle_dir / "task-board.json"),
            "introduction-section-polish",
            str(context_dir),
        ],
        check=True,
    )

    json_path = context_dir / "task-context-introduction-section-polish.json"
    md_path = context_dir / "task-context-introduction-section-polish.md"
    assert json_path.exists()
    assert md_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    assert data["mode"] == "task_context_package"
    assert data["task"]["id"] == "introduction-section-polish"
    assert data["source_contexts"][0]["file"] == "sections/introduction.tex"
    assert "Prior work" in data["source_contexts"][0]["text"]
    assert "# Task Context" in markdown
    assert "introduction-section-polish" in markdown
    assert "## Source Context" in markdown


def test_prepare_task_context_fails_for_unknown_task(tmp_path):
    bundle_dir = tmp_path / "bundle"
    context_dir = tmp_path / "context"
    subprocess.run(["python", str(REVIEW_BUNDLE), str(PROJECT), str(bundle_dir)], check=True)

    result = subprocess.run(
        ["python", str(SCRIPT), str(bundle_dir / "task-board.json"), "missing-task", str(context_dir)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "task not found: missing-task" in result.stderr
