import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
SCRIPT = ROOT.parent / "scripts" / "validate_writeback.py"


def run_validator(before: str, after: str, tmp_path: Path):
    before_path = tmp_path / "before.tex"
    after_path = tmp_path / "after.tex"
    before_path.write_text(before, encoding="utf-8")
    after_path.write_text(after, encoding="utf-8")
    result = subprocess.run(
        ["python", str(SCRIPT), str(before_path), str(after_path)],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def test_validator_passes_when_construct_counts_match(tmp_path):
    before = "Text~\\cite{a}. See Fig.~\\ref{fig:x}. $n=1$"
    after = "Clearer text~\\cite{a}. See Fig.~\\ref{fig:x}. $n=1$"
    data = run_validator(before, after, tmp_path)
    assert data["ok"] is True
    assert data["warnings"] == []


def test_validator_warns_when_citation_removed(tmp_path):
    before = "Text~\\cite{a}. See Fig.~\\ref{fig:x}."
    after = "Clearer text. See Fig.~\\ref{fig:x}."
    data = run_validator(before, after, tmp_path)
    assert data["ok"] is False
    assert any("cite" in warning for warning in data["warnings"])
