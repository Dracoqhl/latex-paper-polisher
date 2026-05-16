import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PACKAGE = ROOT / "fixtures" / "section-workbench" / "section-polish-package-introduction.json"
VALIDATOR = ROOT.parent / "scripts" / "validate_section_polish_suggestions.py"
MERGER = ROOT.parent / "scripts" / "merge_section_polish_suggestions.py"


def suggestion_payload() -> dict:
    package = json.loads(PACKAGE.read_text(encoding="utf-8"))
    return {
        "schema_version": 1,
        "mode": "section_polish_suggestions",
        "section_id": package["section_id"],
        "section_title": package["section_title"],
        "source_package_ref": str(PACKAGE),
        "items": [
            {
                "item_id": package["items"][0]["item_id"],
                "source_file": package["items"][0]["source_file"],
                "line_range": package["items"][0]["line_range"],
                "original_text": package["items"][0]["original_text"],
                "suggested_text": r"Prior work has examined this topic~\cite{smith2020}. However, existing methods remain limited when $n$ is large.",
                "revision_notes": ["Uses a more academic verb.", "Preserves citation and inline math."],
                "risks": [],
                "questions": [],
            },
            {
                "item_id": package["items"][1]["item_id"],
                "source_file": package["items"][1]["source_file"],
                "line_range": package["items"][1]["line_range"],
                "original_text": package["items"][1]["original_text"],
                "suggested_text": "We propose a compact method that improves robustness while preserving computational efficiency.",
                "revision_notes": ["Adds a more specific benefit."],
                "risks": ["Confirm computational efficiency is supported later."],
                "questions": ["Should this paragraph preview the contribution list?"],
            },
        ],
    }


def write_suggestions(tmp_path: Path, payload: dict | None = None) -> Path:
    path = tmp_path / "section-polish-suggestions.json"
    path.write_text(json.dumps(payload or suggestion_payload(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def test_validate_section_polish_suggestions_accepts_matching_items(tmp_path):
    suggestions_path = write_suggestions(tmp_path)

    result = subprocess.run(
        ["python", str(VALIDATOR), str(PACKAGE), str(suggestions_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    summary = json.loads(result.stdout)
    assert summary["ok"] is True
    assert summary["section_id"] == "introduction"
    assert summary["item_count"] == 2
    assert summary["errors"] == []


def test_validate_section_polish_suggestions_rejects_original_text_mismatch(tmp_path):
    payload = suggestion_payload()
    payload["items"][0]["original_text"] = "Different text."
    suggestions_path = write_suggestions(tmp_path, payload)

    result = subprocess.run(
        ["python", str(VALIDATOR), str(PACKAGE), str(suggestions_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert "items[0].original_text does not match source package" in summary["errors"]


def test_merge_section_polish_suggestions_fills_suggestions_but_keeps_editable_text_original(tmp_path):
    suggestions_path = write_suggestions(tmp_path)
    output_path = tmp_path / "merged-section-package.json"

    subprocess.run(["python", str(MERGER), str(PACKAGE), str(suggestions_path), str(output_path)], check=True)

    merged = json.loads(output_path.read_text(encoding="utf-8"))
    assert merged["mode"] == "section_polish_package"
    assert merged["items"][0]["suggested_text"].startswith("Prior work has examined")
    assert merged["items"][0]["revision_notes"] == ["Uses a more academic verb.", "Preserves citation and inline math."]
    assert merged["items"][0]["editable_text"] == merged["items"][0]["original_text"]
    assert merged["items"][1]["risks"] == ["Confirm computational efficiency is supported later."]
    assert merged["items"][1]["questions"] == ["Should this paragraph preview the contribution list?"]
    assert merged["metadata"]["suggestions_ref"] == str(suggestions_path)
