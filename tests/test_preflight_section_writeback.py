import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PROJECT = ROOT / "fixtures" / "sample-paper"
SCRIPT = ROOT.parent / "scripts" / "preflight_section_writeback.py"


def make_candidate(tmp_path: Path) -> Path:
    candidate = {
        "schema_version": 1,
        "mode": "section_writeback_candidate",
        "section_id": "introduction",
        "section_title": "Introduction",
        "source_file": "sections/introduction.tex",
        "source_files": ["sections/introduction.tex"],
        "items": [
            {
                "item_id": "intro-p001",
                "source_file": "sections/introduction.tex",
                "line_range": [4, 4],
                "original_text": "Prior work has studied this topic~\\cite{smith2020}. However, existing methods are often limited when $n$ is large.",
                "final_text": "Prior work has examined this topic~\\cite{smith2020}. However, existing methods remain limited when $n$ is large.",
            },
            {
                "item_id": "intro-p002",
                "source_file": "sections/introduction.tex",
                "line_range": [6, 6],
                "original_text": "We propose a compact method that improves robustness. The main contribution is a clearer analysis of the failure mode.",
                "final_text": "We propose a compact method that improves robustness. The main contribution is a clearer analysis of the failure mode.",
            },
        ],
        "validation_required": True,
        "source_write_permitted": False,
        "metadata": {"item_count": 2},
    }
    path = tmp_path / "section-writeback-candidate.json"
    path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def test_preflight_section_writeback_passes_for_exact_single_matches(tmp_path):
    candidate_path = make_candidate(tmp_path)

    result = subprocess.run(
        ["python", str(SCRIPT), str(PROJECT), str(candidate_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    summary = json.loads(result.stdout)
    assert summary["ok"] is True
    assert summary["section_id"] == "introduction"
    assert summary["source_write_permitted"] is False
    assert summary["items"][0]["match_count"] == 1
    assert summary["items"][0]["latex_validation"]["ok"] is True


def test_preflight_section_writeback_rejects_missing_original_text(tmp_path):
    candidate_path = make_candidate(tmp_path)
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate["items"][0]["original_text"] = "This original text is not in the source."
    candidate_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(
        ["python", str(SCRIPT), str(PROJECT), str(candidate_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert summary["ok"] is False
    assert "intro-p001 original_text match count is 0" in summary["errors"]


def test_preflight_section_writeback_rejects_multiple_original_matches(tmp_path):
    candidate_path = make_candidate(tmp_path)
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate["items"] = [candidate["items"][0]]
    candidate["items"][0]["original_text"] = "method"
    candidate["items"][0]["final_text"] = "approach"
    candidate_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(
        ["python", str(SCRIPT), str(PROJECT), str(candidate_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert summary["ok"] is False
    assert "intro-p001 original_text match count is 3" in summary["errors"]


def test_preflight_section_writeback_rejects_latex_construct_changes(tmp_path):
    candidate_path = make_candidate(tmp_path)
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate["items"][0]["final_text"] = "Prior work has examined this topic. However, existing methods remain limited."
    candidate_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(
        ["python", str(SCRIPT), str(PROJECT), str(candidate_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert "intro-p001: cite count changed from 1 to 0" in summary["errors"]
    assert "intro-p001: inline_math count changed from 1 to 0" in summary["errors"]


def test_preflight_section_writeback_writes_optional_report_file(tmp_path):
    candidate_path = make_candidate(tmp_path)
    report_path = tmp_path / "preflight-report.json"

    subprocess.run(
        ["python", str(SCRIPT), str(PROJECT), str(candidate_path), str(report_path)],
        check=True,
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert report["mode"] == "section_writeback_preflight"
    assert report["source_write_permitted"] is False
