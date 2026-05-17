import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
SCRIPT = ROOT.parent / "scripts" / "record_terminal_polish_session.py"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def valid_session() -> dict:
    return {
        "timestamp": "2026-05-17T10:00:00Z",
        "paper_root": "/paper",
        "target_section": "Abstract",
        "semantic_unit": "opening motivation sentence",
        "source_files_touched": ["main.tex"],
        "original_excerpt": "Original abstract sentence.",
        "final_excerpt": "Revised abstract sentence.",
        "user_confirmation": "Use the revised sentence.",
        "validation": {
            "commands": ["python scripts/validate_writeback.py before.tex after.tex"],
            "summary": "LaTeX constructs preserved.",
            "ok": True,
        },
        "paper_commit_hash": "abc1234",
        "knowledge_updates": ["Prefer concise abstract motivation."],
    }


def test_records_terminal_polish_session_jsonl(tmp_path):
    input_path = tmp_path / "session.json"
    log_path = tmp_path / "terminal-polish.jsonl"
    input_path.write_text(json.dumps(valid_session()), encoding="utf-8")

    subprocess.run(["python", str(SCRIPT), str(input_path), str(log_path)], check=True)

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["schema_version"] == 1
    assert record["mode"] == "terminal_polish_session"
    assert record["target_section"] == "Abstract"
    assert record["semantic_unit"] == "opening motivation sentence"
    assert record["source_files_touched"] == ["main.tex"]
    assert record["original_excerpt_hash"] == sha256_text("Original abstract sentence.")
    assert record["final_excerpt_hash"] == sha256_text("Revised abstract sentence.")
    assert "original_excerpt" not in record
    assert "final_excerpt" not in record
    assert record["validation"]["ok"] is True
    assert record["paper_commit_hash"] == "abc1234"
    assert record["knowledge_updates"] == ["Prefer concise abstract motivation."]


def test_appends_multiple_terminal_polish_sessions(tmp_path):
    input_path = tmp_path / "session.json"
    log_path = tmp_path / "terminal-polish.jsonl"
    input_path.write_text(json.dumps(valid_session()), encoding="utf-8")

    subprocess.run(["python", str(SCRIPT), str(input_path), str(log_path)], check=True)
    subprocess.run(["python", str(SCRIPT), str(input_path), str(log_path)], check=True)

    assert len(log_path.read_text(encoding="utf-8").splitlines()) == 2


def test_rejects_missing_required_session_fields(tmp_path):
    session = valid_session()
    del session["paper_commit_hash"]
    input_path = tmp_path / "session.json"
    log_path = tmp_path / "terminal-polish.jsonl"
    input_path.write_text(json.dumps(session), encoding="utf-8")

    result = subprocess.run(
        ["python", str(SCRIPT), str(input_path), str(log_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert not log_path.exists()
    assert "missing required terminal session keys: paper_commit_hash" in result.stderr
