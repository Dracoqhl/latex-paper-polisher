import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PACKAGE = ROOT / "fixtures" / "section-workbench" / "section-polish-package-introduction.json"
SCRIPT = ROOT.parent / "scripts" / "prepare_section_workbench_from_suggestions.py"


def write_suggestions(tmp_path: Path, *, mismatch: bool = False) -> Path:
    package = json.loads(PACKAGE.read_text(encoding="utf-8"))
    first = package["items"][0]
    second = package["items"][1]
    if mismatch:
        first = {**first, "original_text": "Different source text."}
    payload = {
        "schema_version": 1,
        "mode": "section_polish_suggestions",
        "section_id": package["section_id"],
        "section_title": package["section_title"],
        "source_package_ref": str(PACKAGE),
        "items": [
            {
                "item_id": first["item_id"],
                "source_file": first["source_file"],
                "line_range": first["line_range"],
                "original_text": first["original_text"],
                "suggested_text": r"Prior work has examined this topic~\cite{smith2020}. However, existing methods remain limited when $n$ is large.",
                "revision_notes": ["Uses a more precise academic verb."],
                "risks": [],
                "questions": [],
            },
            {
                "item_id": second["item_id"],
                "source_file": second["source_file"],
                "line_range": second["line_range"],
                "original_text": second["original_text"],
                "suggested_text": "We propose a compact method that improves robustness while preserving computational efficiency.",
                "revision_notes": ["Adds a more specific benefit."],
                "risks": ["Confirm computational efficiency is supported later."],
                "questions": [],
            },
        ],
    }
    path = tmp_path / "section-polish-suggestions.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def test_prepare_section_workbench_from_suggestions_merges_and_builds_html(tmp_path):
    suggestions_path = write_suggestions(tmp_path)
    merged_path = tmp_path / "merged-section-package.json"
    html_path = tmp_path / "section-workbench.html"

    result = subprocess.run(
        ["python", str(SCRIPT), str(PACKAGE), str(suggestions_path), str(merged_path), str(html_path)],
        text=True,
        capture_output=True,
        check=True,
    )

    summary = json.loads(result.stdout)
    assert summary["ok"] is True
    assert summary["section_id"] == "introduction"
    assert summary["merged_package"] == str(merged_path)
    assert summary["html"] == str(html_path)
    assert summary["item_count"] == 2
    assert summary["errors"] == []

    merged = json.loads(merged_path.read_text(encoding="utf-8"))
    assert merged["items"][0]["suggested_text"].startswith("Prior work has examined")
    assert merged["items"][0]["editable_text"] == merged["items"][0]["original_text"]

    html = html_path.read_text(encoding="utf-8")
    assert "Prior work has examined" in html
    assert "downloadSectionFinalEdits" in html


def test_prepare_section_workbench_from_suggestions_stops_on_invalid_suggestions(tmp_path):
    suggestions_path = write_suggestions(tmp_path, mismatch=True)
    merged_path = tmp_path / "merged-section-package.json"
    html_path = tmp_path / "section-workbench.html"

    result = subprocess.run(
        ["python", str(SCRIPT), str(PACKAGE), str(suggestions_path), str(merged_path), str(html_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert summary["ok"] is False
    assert "items[0].original_text does not match source package" in summary["errors"]
    assert not merged_path.exists()
    assert not html_path.exists()
