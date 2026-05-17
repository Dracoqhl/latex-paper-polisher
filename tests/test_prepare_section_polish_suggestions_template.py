import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PACKAGE = ROOT / "fixtures" / "section-polish" / "section-polish-package-introduction.json"
SCRIPT = ROOT.parent / "scripts" / "prepare_section_polish_suggestions_template.py"
VALIDATOR = ROOT.parent / "scripts" / "validate_section_polish_suggestions.py"


def test_prepare_section_polish_suggestions_template_from_section_package(tmp_path):
    output_path = tmp_path / "section-polish-suggestions-template.json"

    subprocess.run(["python", str(SCRIPT), str(PACKAGE), str(output_path)], check=True)

    template = json.loads(output_path.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE.read_text(encoding="utf-8"))
    assert template["schema_version"] == 1
    assert template["mode"] == "section_polish_suggestions"
    assert template["section_id"] == package["section_id"]
    assert template["section_title"] == package["section_title"]
    assert template["source_package_ref"] == str(PACKAGE)
    assert template["paper_context"] == package.get("paper_context", {})
    assert len(template["items"]) == len(package["items"])
    assert template["items"][0]["item_id"] == package["items"][0]["item_id"]
    assert template["items"][0]["source_file"] == package["items"][0]["source_file"]
    assert template["items"][0]["line_range"] == package["items"][0]["line_range"]
    assert template["items"][0]["original_text"] == package["items"][0]["original_text"]
    assert template["items"][0]["suggested_text"] == ""
    assert template["items"][0]["revision_notes"] == []
    assert template["items"][0]["risks"] == []
    assert template["items"][0]["questions"] == []
    assert "editable_text" not in template["items"][0]


def test_generated_suggestions_template_fails_validation_until_specialist_fills_text(tmp_path):
    output_path = tmp_path / "section-polish-suggestions-template.json"
    subprocess.run(["python", str(SCRIPT), str(PACKAGE), str(output_path)], check=True)

    result = subprocess.run(
        ["python", str(VALIDATOR), str(PACKAGE), str(output_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert "items[0].suggested_text must not be empty" in summary["errors"]
