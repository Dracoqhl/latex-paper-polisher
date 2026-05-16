import json
import subprocess
from pathlib import Path

from test_prepare_writeback_candidate import make_decision


ROOT = Path(__file__).parent
PAYLOAD_SCRIPT = ROOT.parent / "scripts" / "prepare_workbench_payload.py"
WORKBENCH = ROOT.parent / "scripts" / "build_workbench.py"
WRITEBACK_CANDIDATE = ROOT.parent / "scripts" / "prepare_writeback_candidate.py"
SCRIPT = ROOT.parent / "scripts" / "prepare_workbench_review_state.py"


def make_payload_decision_and_candidate(tmp_path: Path) -> tuple[Path, Path, Path]:
    decision_path = make_decision(tmp_path, "accept")
    candidate_path = tmp_path / "candidate.json"
    subprocess.run(["python", str(WRITEBACK_CANDIDATE), str(decision_path), str(candidate_path)], check=True)

    payload_path = tmp_path / "workbench-payload.json"
    # The decision fixture helper already generated this payload next to the decision input.
    assert payload_path.exists()
    return payload_path, decision_path, candidate_path


def test_prepare_workbench_review_state_merges_decision_and_candidate(tmp_path):
    payload_path, decision_path, candidate_path = make_payload_decision_and_candidate(tmp_path)
    output_path = tmp_path / "workbench-review-state.json"

    subprocess.run(
        ["python", str(SCRIPT), str(payload_path), str(decision_path), str(candidate_path), str(output_path)],
        check=True,
    )

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["paragraph_id"] == "introduction-section-polish"
    assert data["review_status"]["decision"] == "accept"
    assert data["review_status"]["ready_for_writeback"] is True
    assert data["writeback_candidate"]["available"] is True
    assert data["writeback_candidate"]["validation_required"] is True
    assert data["writeback_candidate"]["source_write_permitted"] is False
    assert any("prepare_writeback_candidate.py" in item for item in data["next_commands"])
    assert any("Future writeback must still be explicitly approved" in item for item in data["next_commands"])


def test_review_state_payload_builds_html_with_status_and_commands(tmp_path):
    payload_path, decision_path, candidate_path = make_payload_decision_and_candidate(tmp_path)
    output_path = tmp_path / "workbench-review-state.json"
    html_path = tmp_path / "workbench.html"

    subprocess.run(
        ["python", str(SCRIPT), str(payload_path), str(decision_path), str(candidate_path), str(output_path)],
        check=True,
    )
    subprocess.run(["python", str(WORKBENCH), str(output_path), str(html_path)], check=True)

    html = html_path.read_text(encoding="utf-8")
    assert "Review Status" in html
    assert "Decision: accept" in html
    assert "Candidate available: true" in html
    assert "Next Commands" in html
    assert "prepare_writeback_candidate.py" in html
