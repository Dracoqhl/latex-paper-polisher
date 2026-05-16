import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
SCRIPT = ROOT.parent / "scripts" / "build_paper_overview.py"


def write_summary(tmp_path: Path) -> Path:
    summary = {
        "schema_version": 1,
        "mode": "paper_summary",
        "project_root": "/example/arxiv-test",
        "main_file": "example_paper.tex",
        "thesis": "The paper argues that heatmap-guided MCTS is less practically effective than expected for large-scale TSPs.",
        "contributions": [
            "Critiques ML-based heatmap generation for large-scale TSP.",
            "Introduces SoftDist as a simple baseline.",
        ],
        "section_map": [
            {
                "section_id": "introduction",
                "title": "Introduction",
                "source_file": "example_paper.tex",
                "role": "Motivates the position and states contributions.",
            },
            {
                "section_id": "experiments",
                "title": "Experiments",
                "source_file": "example_paper.tex",
                "role": "Provides empirical evidence against heatmap-guided MCTS effectiveness.",
            },
        ],
        "terminology": ["SoftDist", "heatmap-guided MCTS", "Score metric"],
        "macro_risks": ["Avoid overstating SoftDist as a new solver rather than a baseline."],
        "structural_suggestions": ["Clarify the relation between SoftDist and the later OURS row."],
        "polishing_guidance": [
            "Preserve LaTeX citations, labels, refs, math, comments, and environments.",
            "Prefer precise academic English over stronger unsupported claims.",
        ],
    }
    path = tmp_path / "paper-summary.json"
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def test_build_paper_overview_html_from_valid_summary(tmp_path):
    summary_path = write_summary(tmp_path)
    output_path = tmp_path / "paper-overview.html"

    result = subprocess.run(["python", str(SCRIPT), str(summary_path), str(output_path)], text=True, capture_output=True, check=True)

    status = json.loads(result.stdout)
    assert status["ok"] is True
    assert status["output"] == str(output_path)
    assert status["section_count"] == 2

    html = output_path.read_text(encoding="utf-8")
    assert "Paper Overview" in html
    assert "example_paper.tex" in html
    assert "heatmap-guided MCTS" in html
    assert "SoftDist" in html
    assert "Score metric" in html
    assert "Motivates the position" in html
    assert "Clarify the relation" in html


def test_build_paper_overview_rejects_unvalidated_summary(tmp_path):
    summary_path = write_summary(tmp_path)
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    data["thesis"] = ""
    summary_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    output_path = tmp_path / "paper-overview.html"

    result = subprocess.run(["python", str(SCRIPT), str(summary_path), str(output_path)], text=True, capture_output=True)

    assert result.returncode == 1
    status = json.loads(result.stdout)
    assert status["ok"] is False
    assert "thesis must not be empty" in status["errors"]
    assert not output_path.exists()
