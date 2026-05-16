import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PROJECT = ROOT / "fixtures" / "sample-paper"
INSPECTOR = ROOT.parent / "scripts" / "inspect_latex_project.py"
PAPER_TEMPLATE = ROOT.parent / "scripts" / "prepare_paper_summary_template.py"
SECTION_TEMPLATE = ROOT.parent / "scripts" / "prepare_section_polish_package_template.py"


def build_inputs(tmp_path: Path) -> tuple[Path, Path]:
    inspection_path = tmp_path / "inspection.json"
    inspected = subprocess.run(
        ["python", str(INSPECTOR), str(PROJECT)],
        check=True,
        text=True,
        capture_output=True,
    )
    inspection_path.write_text(inspected.stdout, encoding="utf-8")

    map_path = tmp_path / "project-map.json"
    mapped = subprocess.run(
        ["python", str(INSPECTOR), "--map", str(PROJECT)],
        check=True,
        text=True,
        capture_output=True,
    )
    map_path.write_text(mapped.stdout, encoding="utf-8")

    summary_path = tmp_path / "paper-summary.json"
    subprocess.run(["python", str(PAPER_TEMPLATE), str(map_path), str(summary_path)], check=True)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["thesis"] = "The paper studies a sample method."
    summary["contributions"] = ["Introduces a compact method."]
    summary["section_map"][0]["role"] = "Motivates the problem and states the contribution."
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return inspection_path, summary_path


def test_prepare_section_polish_package_template_from_summary_and_inspection(tmp_path):
    inspection_path, summary_path = build_inputs(tmp_path)
    output_path = tmp_path / "section-polish-package-introduction.json"

    subprocess.run(
        ["python", str(SECTION_TEMPLATE), str(inspection_path), str(summary_path), "introduction", str(output_path)],
        check=True,
    )

    package = json.loads(output_path.read_text(encoding="utf-8"))
    assert package["schema_version"] == 1
    assert package["mode"] == "section_polish_package"
    assert package["section_id"] == "introduction"
    assert package["section_title"] == "Introduction"
    assert package["source_file"] == "sections/introduction.tex"
    assert package["paper_summary_ref"] == str(summary_path)
    assert package["paper_context"]["thesis"] == "The paper studies a sample method."
    assert package["paper_context"]["section_role"] == "Motivates the problem and states the contribution."
    assert [item["item_id"] for item in package["items"]] == ["introduction-p001", "introduction-p002", "introduction-c001"]
    assert package["items"][0]["line_range"] == [4, 4]
    assert package["items"][0]["original_text"].startswith("Prior work has studied")
    assert package["items"][0]["suggested_text"] == ""
    assert package["items"][0]["revision_notes"] == []
    assert package["items"][0]["editable_text"] == package["items"][0]["original_text"]
    assert package["items"][2]["item_type"] == "caption"
    assert package["items"][2]["risks"] == ["Contains CJK or full-width characters detected by inspection."]


def test_prepare_section_polish_package_template_rejects_unknown_section(tmp_path):
    inspection_path, summary_path = build_inputs(tmp_path)
    output_path = tmp_path / "missing.json"

    result = subprocess.run(
        ["python", str(SECTION_TEMPLATE), str(inspection_path), str(summary_path), "related-work", str(output_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert summary["ok"] is False
    assert "section_id not found in paper summary: related-work" in summary["errors"]
    assert not output_path.exists()
