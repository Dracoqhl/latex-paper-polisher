import json
import subprocess
from pathlib import Path

from test_prepare_workbench_payload import build_valid_suggestion


ROOT = Path(__file__).parent
PAYLOAD = ROOT.parent / "scripts" / "prepare_workbench_payload.py"
SCRIPT = ROOT.parent / "scripts" / "record_review_decision.py"


def build_workbench_payload(tmp_path: Path) -> Path:
    context_path, suggestion_path = build_valid_suggestion(tmp_path)
    payload_path = tmp_path / "workbench-payload.json"
    subprocess.run(["python", str(PAYLOAD), str(context_path), str(suggestion_path), str(payload_path)], check=True)
    return payload_path


def test_records_accept_decision_with_suggested_text(tmp_path):
    payload_path = build_workbench_payload(tmp_path)
    decision_path = tmp_path / "decision.json"

    subprocess.run(
        [
            "python",
            str(SCRIPT),
            str(payload_path),
            "accept",
            "Main agent accepts specialist suggestion.",
            str(decision_path),
        ],
        check=True,
    )

    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    assert decision["schema_version"] == 1
    assert decision["mode"] == "main_agent_review_decision"
    assert decision["decision"] == "accept"
    assert decision["paragraph_id"] == payload["paragraph_id"]
    assert decision["source_file"] == payload["source_file"]
    assert decision["final_text"] == payload["suggested_text"]
    assert decision["ready_for_writeback"] is True
    assert decision["review_notes"] == "Main agent accepts specialist suggestion."


def test_records_revise_decision_with_explicit_final_text(tmp_path):
    payload_path = build_workbench_payload(tmp_path)
    decision_path = tmp_path / "decision.json"
    final_text = "Main-agent revised final text."

    subprocess.run(
        [
            "python",
            str(SCRIPT),
            str(payload_path),
            "revise",
            "Main agent revised wording before user review.",
            str(decision_path),
            "--final-text",
            final_text,
        ],
        check=True,
    )

    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    assert decision["decision"] == "revise"
    assert decision["final_text"] == final_text
    assert decision["ready_for_writeback"] is True


def test_records_reject_decision_without_writeback_ready(tmp_path):
    payload_path = build_workbench_payload(tmp_path)
    decision_path = tmp_path / "decision.json"

    subprocess.run(
        [
            "python",
            str(SCRIPT),
            str(payload_path),
            "reject",
            "Suggestion changes meaning.",
            str(decision_path),
        ],
        check=True,
    )

    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    assert decision["decision"] == "reject"
    assert decision["final_text"] == ""
    assert decision["ready_for_writeback"] is False


def test_revise_requires_final_text(tmp_path):
    payload_path = build_workbench_payload(tmp_path)
    decision_path = tmp_path / "decision.json"

    result = subprocess.run(
        ["python", str(SCRIPT), str(payload_path), "revise", "Needs revised text.", str(decision_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert not decision_path.exists()
    assert "revise requires --final-text" in result.stderr
