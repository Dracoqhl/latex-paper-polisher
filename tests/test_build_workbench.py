import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
SCRIPT = ROOT.parent / "scripts" / "build_workbench.py"
ASSETS = ROOT.parent / "assets" / "workbench"


def test_builds_current_paragraph_html(tmp_path):
    payload = {
        "paragraph_id": "sections/introduction.tex:paragraph:1",
        "source_file": "sections/introduction.tex",
        "section": "Introduction",
        "original_text": "This paper studies a sample problem， and proposes a method.",
        "suggested_text": "This paper studies a sample problem and proposes a method.",
        "rationale": ["Replaced Chinese comma with an English comma.", "Improved academic fluency."],
        "warnings": ["Chinese punctuation detected."],
    }
    payload_path = tmp_path / "payload.json"
    output_path = tmp_path / "workbench.html"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")

    subprocess.run(
        ["python", str(SCRIPT), str(payload_path), str(output_path)],
        check=True,
    )

    html = output_path.read_text(encoding="utf-8")
    assert "Current Paragraph" in html
    assert "Original" in html
    assert "Suggested Revision" in html
    assert "Chinese punctuation detected." in html
    assert "sections/introduction.tex:paragraph:1" in html


def test_workbench_assets_are_skill_owned():
    assert (ASSETS / "workbench.html").exists()
    assert (ASSETS / "workbench.css").exists()
    assert (ASSETS / "workbench.js").exists()


def test_builds_interactive_decision_controls(tmp_path):
    payload = {
        "paragraph_id": "introduction-section-polish",
        "source_file": "sections/introduction.tex",
        "section": "Introduction",
        "original_text": "Original text.",
        "suggested_text": "Suggested text.",
        "rationale": ["Reason."],
        "warnings": [],
        "review_status": {"decision": "pending", "ready_for_writeback": False, "review_notes": ""},
        "writeback_candidate": {"available": False, "validation_required": True, "source_write_permitted": False},
        "next_commands": ["python scripts/record_review_decision.py ..."],
    }
    payload_path = tmp_path / "payload.json"
    output_path = tmp_path / "workbench.html"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")

    subprocess.run(["python", str(SCRIPT), str(payload_path), str(output_path)], check=True)

    html = output_path.read_text(encoding="utf-8")
    assert '<script id="workbench-payload" type="application/json">' in html
    assert 'id="accept-decision"' in html
    assert 'id="revise-decision"' in html
    assert 'id="reject-decision"' in html
    assert 'id="final-text"' in html
    assert "downloadDecisionJson" in html
    assert "record_review_decision.py" in html
