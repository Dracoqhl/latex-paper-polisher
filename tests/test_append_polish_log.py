import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
SCRIPT = ROOT.parent / "scripts" / "append_polish_log.py"


def test_appends_jsonl_entry(tmp_path):
    entry = {
        "timestamp": "2026-05-14T00:00:00Z",
        "project_path": "/paper",
        "source_file": "main.tex",
        "section": "Abstract",
        "paragraph_id": "main.tex:paragraph:1",
        "original_text": "Original.",
        "suggested_text": "Suggested.",
        "user_feedback": "Accepted.",
        "final_writeback_text": "Suggested.",
        "diff_summary": "One paragraph changed.",
        "validation_result": {"ok": True, "warnings": []},
        "commit_hash": "abc1234",
        "knowledge_updates": [],
    }
    entry_path = tmp_path / "entry.json"
    log_path = tmp_path / "polish.jsonl"
    entry_path.write_text(json.dumps(entry), encoding="utf-8")

    subprocess.run(["python", str(SCRIPT), str(entry_path), str(log_path)], check=True)
    subprocess.run(["python", str(SCRIPT), str(entry_path), str(log_path)], check=True)

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["paragraph_id"] == "main.tex:paragraph:1"
