import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PACKAGE = ROOT / "fixtures" / "section-workbench" / "section-polish-package-introduction.json"
SCRIPT = ROOT.parent / "scripts" / "build_section_workbench.py"


def test_builds_section_workbench_html(tmp_path):
    output_path = tmp_path / "section-workbench.html"

    subprocess.run(["python", str(SCRIPT), str(PACKAGE), str(output_path)], check=True)

    html = output_path.read_text(encoding="utf-8")
    assert "Section Workbench" in html
    assert "Introduction" in html
    assert "intro-p001" in html
    assert "Previous Paragraph" in html
    assert "Next Paragraph" in html
    assert "Submit Whole Section" in html
    assert "copy-original" in html
    assert "copy-suggested" in html
    assert "final-text" in html
    assert "agent-discussion" in html
    assert "downloadSectionFinalEdits" in html
    assert "section-polish-package" in html


def test_section_workbench_embeds_package_json_safely(tmp_path):
    output_path = tmp_path / "section-workbench.html"

    subprocess.run(["python", str(SCRIPT), str(PACKAGE), str(output_path)], check=True)

    html = output_path.read_text(encoding="utf-8")
    assert '<script id="section-polish-package" type="application/json">' in html
    assert "\\u003c" not in html
    assert "editable_text" in html
