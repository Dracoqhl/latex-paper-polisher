import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PACKAGE = ROOT / "fixtures" / "section-workbench" / "section-polish-package-introduction.json"
SCRIPT = ROOT.parent / "scripts" / "validate_section_final_edits.py"


def make_final_edits(tmp_path: Path) -> Path:
    package = json.loads(PACKAGE.read_text(encoding="utf-8"))
    edits = {
        "schema_version": 1,
        "mode": "section_final_edits",
        "section_id": package["section_id"],
        "section_title": package["section_title"],
        "items": [
            {
                "item_id": item["item_id"],
                "source_file": item["source_file"],
                "line_range": item["line_range"],
                "original_text": item["original_text"],
                "final_text": item["editable_text"],
            }
            for item in package["items"]
        ],
    }
    path = tmp_path / "section-final-edits.json"
    path.write_text(json.dumps(edits, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def test_valid_section_final_edits_pass(tmp_path):
    edits_path = make_final_edits(tmp_path)

    result = subprocess.run(
        ["python", str(SCRIPT), str(PACKAGE), str(edits_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    summary = json.loads(result.stdout)
    assert summary["ok"] is True
    assert summary["section_id"] == "introduction"
    assert summary["item_count"] == 2
    assert summary["errors"] == []


def test_rejects_original_text_mismatch(tmp_path):
    edits_path = make_final_edits(tmp_path)
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    edits["items"][0]["original_text"] = "Different original text."
    edits_path.write_text(json.dumps(edits, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(
        ["python", str(SCRIPT), str(PACKAGE), str(edits_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert "items[0].original_text does not match section package" in summary["errors"]


def test_rejects_missing_or_reordered_items(tmp_path):
    edits_path = make_final_edits(tmp_path)
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    edits["items"].reverse()
    edits_path.write_text(json.dumps(edits, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(
        ["python", str(SCRIPT), str(PACKAGE), str(edits_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert "items must preserve section package item order" in summary["errors"]


def test_rejects_empty_final_text(tmp_path):
    edits_path = make_final_edits(tmp_path)
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    edits["items"][1]["final_text"] = ""
    edits_path.write_text(json.dumps(edits, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(
        ["python", str(SCRIPT), str(PACKAGE), str(edits_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert "items[1].final_text must not be empty" in summary["errors"]
