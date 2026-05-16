import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
FIXTURE = ROOT / "fixtures" / "section-workbench" / "section-polish-package-introduction.json"
SCRIPT = ROOT.parent / "scripts" / "validate_section_polish_package.py"


def test_valid_section_polish_package_passes():
    result = subprocess.run(
        ["python", str(SCRIPT), str(FIXTURE)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    summary = json.loads(result.stdout)
    assert summary["ok"] is True
    assert summary["section_id"] == "introduction"
    assert summary["item_count"] == 2
    assert summary["errors"] == []


def test_rejects_editable_text_that_does_not_default_to_original(tmp_path):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["items"][0]["editable_text"] = data["items"][0]["suggested_text"]
    path = tmp_path / "bad-package.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(
        ["python", str(SCRIPT), str(path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert summary["ok"] is False
    assert "items[0].editable_text must equal original_text by default" in summary["errors"]


def test_rejects_missing_required_item_field(tmp_path):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    del data["items"][1]["revision_notes"]
    path = tmp_path / "bad-package.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(
        ["python", str(SCRIPT), str(path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert "items[1] missing required field: revision_notes" in summary["errors"]
