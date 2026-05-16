import json
import subprocess
from pathlib import Path

from test_record_review_decision import build_workbench_payload


ROOT = Path(__file__).parent
REVIEW_DECISION = ROOT.parent / "scripts" / "record_review_decision.py"
SCRIPT = ROOT.parent / "scripts" / "prepare_writeback_candidate.py"


def make_decision(tmp_path: Path, decision: str, final_text: str | None = None) -> Path:
    payload_path = build_workbench_payload(tmp_path)
    decision_path = tmp_path / f"{decision}-decision.json"
    command = [
        "python",
        str(REVIEW_DECISION),
        str(payload_path),
        decision,
        f"Decision for {decision}.",
        str(decision_path),
    ]
    if final_text is not None:
        command.extend(["--final-text", final_text])
    subprocess.run(command, check=True)
    return decision_path


def test_prepare_writeback_candidate_from_accept_decision(tmp_path):
    decision_path = make_decision(tmp_path, "accept")
    candidate_path = tmp_path / "candidate.json"

    subprocess.run(["python", str(SCRIPT), str(decision_path), str(candidate_path)], check=True)

    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    assert candidate["schema_version"] == 1
    assert candidate["mode"] == "writeback_candidate"
    assert candidate["paragraph_id"] == decision["paragraph_id"]
    assert candidate["source_file"] == decision["source_file"]
    assert candidate["original_text"] == decision["original_text"]
    assert candidate["final_text"] == decision["final_text"]
    assert candidate["validation_required"] is True
    assert candidate["source_write_permitted"] is False


def test_prepare_writeback_candidate_from_revise_decision(tmp_path):
    decision_path = make_decision(tmp_path, "revise", "Main-agent revised final text.")
    candidate_path = tmp_path / "candidate.json"

    subprocess.run(["python", str(SCRIPT), str(decision_path), str(candidate_path)], check=True)

    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    assert candidate["final_text"] == "Main-agent revised final text."
    assert candidate["decision"] == "revise"


def test_prepare_writeback_candidate_rejects_rejected_decision(tmp_path):
    decision_path = make_decision(tmp_path, "reject")
    candidate_path = tmp_path / "candidate.json"

    result = subprocess.run(
        ["python", str(SCRIPT), str(decision_path), str(candidate_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert not candidate_path.exists()
    assert "decision is not ready for writeback" in result.stderr


def test_prepare_writeback_candidate_rejects_empty_final_text(tmp_path):
    decision_path = make_decision(tmp_path, "accept")
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    decision["final_text"] = ""
    decision_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
    candidate_path = tmp_path / "candidate.json"

    result = subprocess.run(
        ["python", str(SCRIPT), str(decision_path), str(candidate_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert not candidate_path.exists()
    assert "final_text must not be empty" in result.stderr
