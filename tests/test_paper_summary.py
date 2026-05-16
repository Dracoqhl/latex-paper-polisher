import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PROJECT = ROOT / "fixtures" / "sample-paper"
MAPPER = ROOT.parent / "scripts" / "inspect_latex_project.py"
TEMPLATE = ROOT.parent / "scripts" / "prepare_paper_summary_template.py"
VALIDATOR = ROOT.parent / "scripts" / "validate_paper_summary.py"


def build_project_map(tmp_path: Path) -> Path:
    map_path = tmp_path / "project-map.json"
    mapped = subprocess.run(
        ["python", str(MAPPER), "--map", str(PROJECT)],
        check=True,
        text=True,
        capture_output=True,
    )
    map_path.write_text(mapped.stdout, encoding="utf-8")
    return map_path


def test_prepare_paper_summary_template_from_project_map(tmp_path):
    map_path = build_project_map(tmp_path)
    output_path = tmp_path / "paper-summary.json"

    subprocess.run(["python", str(TEMPLATE), str(map_path), str(output_path)], check=True)

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["mode"] == "paper_summary"
    assert data["project_root"] == str(PROJECT.resolve())
    assert data["main_file"] == "main.tex"
    assert data["thesis"] == ""
    assert data["section_map"][0]["section_id"] == "introduction"
    assert data["section_map"][0]["source_file"] == "sections/introduction.tex"
    assert data["polishing_guidance"] == [
        "Preserve LaTeX citations, labels, refs, math, comments, and environments.",
        "Prefer precise academic English over stronger unsupported claims.",
    ]


def test_validate_paper_summary_accepts_completed_summary(tmp_path):
    map_path = build_project_map(tmp_path)
    summary_path = tmp_path / "paper-summary.json"
    subprocess.run(["python", str(TEMPLATE), str(map_path), str(summary_path)], check=True)

    data = json.loads(summary_path.read_text(encoding="utf-8"))
    data["thesis"] = "The paper studies a sample problem."
    data["contributions"] = ["Introduces a compact method."]
    data["terminology"] = ["compact method"]
    data["macro_risks"] = ["Avoid overstating robustness."]
    data["structural_suggestions"] = ["Clarify the contribution list."]
    summary_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(["python", str(VALIDATOR), str(summary_path)], text=True, capture_output=True)

    assert result.returncode == 0
    summary = json.loads(result.stdout)
    assert summary["ok"] is True
    assert summary["section_count"] == 1
    assert summary["errors"] == []


def test_validate_paper_summary_rejects_unfilled_thesis(tmp_path):
    map_path = build_project_map(tmp_path)
    summary_path = tmp_path / "paper-summary.json"
    subprocess.run(["python", str(TEMPLATE), str(map_path), str(summary_path)], check=True)

    result = subprocess.run(["python", str(VALIDATOR), str(summary_path)], text=True, capture_output=True)

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert "thesis must not be empty" in summary["errors"]


def test_validate_paper_summary_rejects_bad_section_map(tmp_path):
    map_path = build_project_map(tmp_path)
    summary_path = tmp_path / "paper-summary.json"
    subprocess.run(["python", str(TEMPLATE), str(map_path), str(summary_path)], check=True)
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    data["thesis"] = "A thesis."
    del data["section_map"][0]["role"]
    summary_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(["python", str(VALIDATOR), str(summary_path)], text=True, capture_output=True)

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert "section_map[0] missing required field: role" in summary["errors"]
