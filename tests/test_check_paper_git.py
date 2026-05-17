import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
SCRIPT = ROOT.parent / "scripts" / "check_paper_git.py"


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def make_git_paper(tmp_path: Path) -> Path:
    paper = tmp_path / "paper"
    paper.mkdir()
    subprocess.run(["git", "init", "-b", "main", str(paper)], check=True, capture_output=True)
    (paper / "main.tex").write_text("\\section{Introduction}\nText.\n", encoding="utf-8")
    run_git(paper, "add", "main.tex")
    run_git(paper, "commit", "-m", "init paper")
    return paper


def run_check(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python", str(SCRIPT), str(path)],
        text=True,
        capture_output=True,
    )


def test_reports_clean_paper_git_repo(tmp_path):
    paper = make_git_paper(tmp_path)

    result = run_check(paper)

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["ok"] is True
    assert data["is_git_repo"] is True
    assert data["branch"] == "main"
    assert data["dirty_files"] == []
    assert data["errors"] == []
    assert data["repo_root"] == str(paper)


def test_reports_dirty_files_without_failing(tmp_path):
    paper = make_git_paper(tmp_path)
    (paper / "main.tex").write_text("\\section{Introduction}\nChanged text.\n", encoding="utf-8")
    (paper / "notes.txt").write_text("scratch\n", encoding="utf-8")

    result = run_check(paper)

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["ok"] is True
    assert data["is_git_repo"] is True
    assert data["dirty_files"] == [
        {"status": "M", "path": "main.tex"},
        {"status": "??", "path": "notes.txt"},
    ]


def test_reports_non_git_directory(tmp_path):
    paper = tmp_path / "not-git"
    paper.mkdir()
    (paper / "main.tex").write_text("\\section{Introduction}\nText.\n", encoding="utf-8")

    result = run_check(paper)

    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert data["ok"] is False
    assert data["is_git_repo"] is False
    assert data["dirty_files"] == []
    assert "not a git repository" in data["errors"]
