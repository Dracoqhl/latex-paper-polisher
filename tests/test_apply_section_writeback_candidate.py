import json
import shutil
import subprocess
from pathlib import Path

from test_preflight_section_writeback import make_candidate


ROOT = Path(__file__).parent
PROJECT = ROOT / "fixtures" / "sample-paper"
SCRIPT = ROOT.parent / "scripts" / "apply_section_writeback_candidate.py"


def copy_project(tmp_path: Path) -> Path:
    project = tmp_path / "sample-paper"
    shutil.copytree(PROJECT, project)
    return project


def test_apply_section_writeback_candidate_dry_run_outputs_diff_without_writing(tmp_path):
    project = copy_project(tmp_path)
    candidate_path = make_candidate(tmp_path)
    source_path = project / "sections" / "introduction.tex"
    before = source_path.read_text(encoding="utf-8")
    report_path = tmp_path / "dry-run-report.json"

    result = subprocess.run(
        ["python", str(SCRIPT), "--dry-run", str(project), str(candidate_path), str(report_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert source_path.read_text(encoding="utf-8") == before
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert report["dry_run"] is True
    assert report["source_write_permitted"] is False
    assert report["files"][0]["source_file"] == "sections/introduction.tex"
    assert "Prior work has examined" in report["files"][0]["unified_diff"]


def test_apply_section_writeback_candidate_requires_dry_run_flag(tmp_path):
    project = copy_project(tmp_path)
    candidate_path = make_candidate(tmp_path)
    report_path = tmp_path / "dry-run-report.json"

    result = subprocess.run(
        ["python", str(SCRIPT), str(project), str(candidate_path), str(report_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 2
    assert not report_path.exists()
    assert "usage:" in result.stderr


def test_apply_section_writeback_candidate_rejects_failed_preflight(tmp_path):
    project = copy_project(tmp_path)
    candidate_path = make_candidate(tmp_path)
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate["items"][0]["original_text"] = "Missing original text."
    candidate_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path = tmp_path / "dry-run-report.json"

    result = subprocess.run(
        ["python", str(SCRIPT), "--dry-run", str(project), str(candidate_path), str(report_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert not report_path.exists()
    summary = json.loads(result.stdout)
    assert summary["ok"] is False
    assert "intro-p001 original_text match count is 0" in summary["errors"]
