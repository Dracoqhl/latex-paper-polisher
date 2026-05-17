import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PROJECT = ROOT / "fixtures" / "sample-paper"
INSPECT = ROOT.parent / "scripts" / "inspect_latex_project.py"
LOGGER = ROOT.parent / "scripts" / "append_polish_log.py"
VALIDATOR = ROOT.parent / "scripts" / "validate_writeback.py"


def test_terminal_first_inspect_validate_log_flow(tmp_path):
    inspected = subprocess.run(
        ["python", str(INSPECT), str(PROJECT)],
        check=True,
        text=True,
        capture_output=True,
    )
    data = json.loads(inspected.stdout)
    paragraph = data["paragraphs"][0]
    final_text = paragraph["text"].replace("However", "However,")

    before_path = tmp_path / "before.tex"
    after_path = tmp_path / "after.tex"
    before_path.write_text(paragraph["text"], encoding="utf-8")
    after_path.write_text(final_text, encoding="utf-8")
    validation = subprocess.run(
        ["python", str(VALIDATOR), str(before_path), str(after_path)],
        check=True,
        text=True,
        capture_output=True,
    )
    validation_data = json.loads(validation.stdout)
    assert validation_data["ok"] is True

    log_entry = {
        "timestamp": "2026-05-14T00:00:00Z",
        "project_path": str(PROJECT),
        "source_file": paragraph["file"],
        "section": "Introduction",
        "paragraph_id": paragraph["id"],
        "original_text": paragraph["text"],
        "suggested_text": final_text,
        "user_feedback": "Accepted.",
        "final_writeback_text": final_text,
        "diff_summary": "One paragraph changed.",
        "validation_result": validation_data,
        "commit_hash": "not-committed-in-test",
        "knowledge_updates": [],
    }
    entry_path = tmp_path / "entry.json"
    log_path = tmp_path / "polish.jsonl"
    entry_path.write_text(json.dumps(log_entry), encoding="utf-8")
    subprocess.run(["python", str(LOGGER), str(entry_path), str(log_path)], check=True)
    assert len(log_path.read_text(encoding="utf-8").splitlines()) == 1
