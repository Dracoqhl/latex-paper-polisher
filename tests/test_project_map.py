import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PROJECT = ROOT / "fixtures" / "sample-paper"
SCRIPT = ROOT.parent / "scripts" / "inspect_latex_project.py"


def run_mapper():
    result = subprocess.run(
        ["python", str(SCRIPT), "--map", str(PROJECT)],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def test_project_map_contains_mechanical_source_fields():
    data = run_mapper()
    assert data["schema_version"] == 2
    assert data["mode"] == "project_map"
    assert data["main_file"] == "main.tex"
    assert "sections/introduction.tex" in data["files"]
    assert data["sections"][0]["title"] == "Introduction"
    assert data["sections"][0]["anchor"]["file"] == "sections/introduction.tex"


def test_project_map_separates_captions_labels_refs_and_citations():
    data = run_mapper()
    assert any(item["key"] == "fig:overview" for item in data["labels"])
    assert any(item["key"] == "smith2020" for item in data["citations"])
    assert any(item["label"] == "fig:overview" for item in data["captions"])


def test_project_map_marks_preamble_as_protected_not_section_task():
    data = run_mapper()
    protected = data["protected_regions"]
    assert any(region["kind"] == "preamble" and region["file"] == "main.tex" for region in protected)
    assert all(section["file"] != "main.tex" for section in data["sections"])
