import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PROJECT = ROOT / "fixtures" / "sample-paper"
REVIEW_BUNDLE = ROOT.parent / "scripts" / "prepare_review_bundle.py"
TASK_CONTEXT = ROOT.parent / "scripts" / "prepare_task_context.py"
TEMPLATE = ROOT.parent / "scripts" / "prepare_suggestion_template.py"
VALIDATOR = ROOT.parent / "scripts" / "validate_specialist_suggestion.py"
TASK_ID = "introduction-section-polish"


def build_task_context(tmp_path: Path) -> Path:
    bundle_dir = tmp_path / "bundle"
    context_dir = tmp_path / "context"
    subprocess.run(["python", str(REVIEW_BUNDLE), str(PROJECT), str(bundle_dir)], check=True)
    subprocess.run(
        ["python", str(TASK_CONTEXT), str(bundle_dir / "task-board.json"), TASK_ID, str(context_dir)],
        check=True,
    )
    return context_dir / f"task-context-{TASK_ID}.json"


def test_prepare_suggestion_template_writes_review_only_json(tmp_path):
    context_path = build_task_context(tmp_path)
    output_path = tmp_path / "suggestion.json"

    subprocess.run(["python", str(TEMPLATE), str(context_path), str(output_path)], check=True)

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["mode"] == "specialist_suggestion"
    assert data["task_id"] == TASK_ID
    assert data["target"]["file"] == "sections/introduction.tex"
    assert data["target"]["line_range"] == [1, 13]
    assert "Prior work" in data["original_text"]
    assert data["proposed_text"] == ""
    assert data["rationale"] == []
    assert data["risks"] == []
    assert data["questions"] == []
    assert data["metadata"]["suggestion_only"] is True


def test_validate_specialist_suggestion_accepts_matching_schema(tmp_path):
    context_path = build_task_context(tmp_path)
    suggestion_path = tmp_path / "suggestion.json"
    subprocess.run(["python", str(TEMPLATE), str(context_path), str(suggestion_path)], check=True)

    data = json.loads(suggestion_path.read_text(encoding="utf-8"))
    data["proposed_text"] = data["original_text"].replace("Prior work has studied", "Prior work has examined")
    data["rationale"] = ["Improves academic word choice while preserving meaning."]
    data["latex_constructs_preserved"] = ["\\cite{smith2020}", "$n$"]
    suggestion_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(
        ["python", str(VALIDATOR), str(context_path), str(suggestion_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    summary = json.loads(result.stdout)
    assert summary["ok"] is True
    assert summary["errors"] == []


def test_validate_specialist_suggestion_rejects_task_and_file_mismatch(tmp_path):
    context_path = build_task_context(tmp_path)
    suggestion_path = tmp_path / "suggestion.json"
    subprocess.run(["python", str(TEMPLATE), str(context_path), str(suggestion_path)], check=True)

    data = json.loads(suggestion_path.read_text(encoding="utf-8"))
    data["task_id"] = "wrong-task"
    data["target"]["file"] = "sections/other.tex"
    data["proposed_text"] = "A revision."
    data["rationale"] = ["A reason."]
    suggestion_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(
        ["python", str(VALIDATOR), str(context_path), str(suggestion_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert summary["ok"] is False
    assert "task_id does not match task context" in summary["errors"]
    assert "target file is not part of task context" in summary["errors"]


def test_validate_specialist_suggestion_rejects_original_text_mismatch(tmp_path):
    context_path = build_task_context(tmp_path)
    suggestion_path = tmp_path / "suggestion.json"
    subprocess.run(["python", str(TEMPLATE), str(context_path), str(suggestion_path)], check=True)

    data = json.loads(suggestion_path.read_text(encoding="utf-8"))
    data["original_text"] = "Different source text."
    data["proposed_text"] = "A revision."
    data["rationale"] = ["A reason."]
    suggestion_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(
        ["python", str(VALIDATOR), str(context_path), str(suggestion_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert "original_text does not match task context" in summary["errors"]
