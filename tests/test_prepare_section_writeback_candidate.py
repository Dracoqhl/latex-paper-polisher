import json
import subprocess
from pathlib import Path

from test_section_final_edits import make_final_edits


ROOT = Path(__file__).parent
PACKAGE = ROOT / "fixtures" / "section-workbench" / "section-polish-package-introduction.json"
SCRIPT = ROOT.parent / "scripts" / "prepare_section_writeback_candidate.py"


def test_prepare_section_writeback_candidate_from_valid_final_edits(tmp_path):
    edits_path = make_final_edits(tmp_path)
    candidate_path = tmp_path / "section-writeback-candidate.json"

    subprocess.run(["python", str(SCRIPT), str(PACKAGE), str(edits_path), str(candidate_path)], check=True)

    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    assert candidate["schema_version"] == 1
    assert candidate["mode"] == "section_writeback_candidate"
    assert candidate["section_id"] == "introduction"
    assert candidate["source_write_permitted"] is False
    assert candidate["validation_required"] is True
    assert len(candidate["items"]) == 2
    assert candidate["items"][0]["item_id"] == edits["items"][0]["item_id"]
    assert candidate["items"][0]["original_text"] == edits["items"][0]["original_text"]
    assert candidate["items"][0]["final_text"] == edits["items"][0]["final_text"]


def test_prepare_section_writeback_candidate_rejects_invalid_final_edits(tmp_path):
    edits_path = make_final_edits(tmp_path)
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    edits["items"][0]["original_text"] = "Changed original."
    edits_path.write_text(json.dumps(edits, ensure_ascii=False, indent=2), encoding="utf-8")
    candidate_path = tmp_path / "section-writeback-candidate.json"

    result = subprocess.run(
        ["python", str(SCRIPT), str(PACKAGE), str(edits_path), str(candidate_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert not candidate_path.exists()
    summary = json.loads(result.stdout)
    assert "items[0].original_text does not match section package" in summary["errors"]


def test_prepare_section_writeback_candidate_groups_items_by_source_file(tmp_path):
    edits_path = make_final_edits(tmp_path)
    candidate_path = tmp_path / "section-writeback-candidate.json"

    subprocess.run(["python", str(SCRIPT), str(PACKAGE), str(edits_path), str(candidate_path)], check=True)

    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    assert candidate["source_files"] == ["sections/introduction.tex"]
    assert candidate["metadata"]["item_count"] == 2


def test_prepare_section_writeback_candidate_reports_missing_input(tmp_path):
    candidate_path = tmp_path / "section-writeback-candidate.json"
    missing_edits = tmp_path / "missing-section-final-edits.json"

    result = subprocess.run(
        ["python", str(SCRIPT), str(PACKAGE), str(missing_edits), str(candidate_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert not candidate_path.exists()
    assert "input file not found" in result.stderr
