import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
SCRIPT = ROOT.parent / "scripts" / "build_workbench.py"


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
