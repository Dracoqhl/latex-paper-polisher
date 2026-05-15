import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PROJECT = ROOT / "fixtures" / "sample-paper"
SCRIPT = ROOT.parent / "scripts" / "inspect_latex_project.py"


def run_inspector():
    result = subprocess.run(
        ["python", str(SCRIPT), str(PROJECT)],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def test_finds_main_file_and_inputs():
    data = run_inspector()
    assert data["main_file"] == "main.tex"
    assert "sections/introduction.tex" in data["files"]


def test_indexes_sections_paragraphs_and_captions():
    data = run_inspector()
    assert data["sections"][0]["title"] == "Introduction"
    paragraphs = data["paragraphs"]
    assert len(paragraphs) == 3
    assert paragraphs[0]["kind"] == "paragraph"
    assert "Prior work" in paragraphs[0]["text"]
    assert paragraphs[2]["kind"] == "caption"
    assert paragraphs[2]["label"] == "fig:overview"


def test_detects_latex_constructs_and_chinese_punctuation():
    data = run_inspector()
    first = data["paragraphs"][0]
    assert first["citations"] == ["smith2020"]
    assert first["math_spans"] == ["$n$"]
    caption = data["paragraphs"][2]
    assert caption["has_cjk_or_fullwidth"] is True
