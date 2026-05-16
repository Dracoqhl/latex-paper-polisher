import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PROJECT = ROOT / "fixtures" / "sample-paper"
REVIEW_BUNDLE = ROOT.parent / "scripts" / "prepare_review_bundle.py"
TASK_CONTEXT = ROOT.parent / "scripts" / "prepare_task_context.py"
SUGGESTION_TEMPLATE = ROOT.parent / "scripts" / "prepare_suggestion_template.py"
SCRIPT = ROOT.parent / "scripts" / "prepare_workbench_payload.py"
WORKBENCH = ROOT.parent / "scripts" / "build_workbench.py"
TASK_ID = "introduction-section-polish"


def build_valid_suggestion(tmp_path: Path) -> tuple[Path, Path]:
    bundle_dir = tmp_path / "bundle"
    context_dir = tmp_path / "context"
    suggestion_path = tmp_path / "suggestion.json"
    subprocess.run(["python", str(REVIEW_BUNDLE), str(PROJECT), str(bundle_dir)], check=True)
    subprocess.run(
        ["python", str(TASK_CONTEXT), str(bundle_dir / "task-board.json"), TASK_ID, str(context_dir)],
        check=True,
    )
    context_path = context_dir / f"task-context-{TASK_ID}.json"
    subprocess.run(["python", str(SUGGESTION_TEMPLATE), str(context_path), str(suggestion_path)], check=True)

    suggestion = json.loads(suggestion_path.read_text(encoding="utf-8"))
    suggestion["proposed_text"] = suggestion["original_text"].replace(
        "Prior work has studied",
        "Prior work has examined",
    )
    suggestion["rationale"] = ["Improves academic word choice while preserving meaning."]
    suggestion["risks"] = ["Main agent should confirm section-level framing."]
    suggestion["questions"] = ["Should the contribution sentence be more specific?"]
    suggestion_path.write_text(json.dumps(suggestion, ensure_ascii=False, indent=2), encoding="utf-8")
    return context_path, suggestion_path


def test_prepare_workbench_payload_from_valid_suggestion(tmp_path):
    context_path, suggestion_path = build_valid_suggestion(tmp_path)
    payload_path = tmp_path / "workbench-payload.json"

    subprocess.run(["python", str(SCRIPT), str(context_path), str(suggestion_path), str(payload_path)], check=True)

    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    assert payload["paragraph_id"] == TASK_ID
    assert payload["source_file"] == "sections/introduction.tex"
    assert payload["section"] == "Polish Introduction"
    assert "Prior work has studied" in payload["original_text"]
    assert "Prior work has examined" in payload["suggested_text"]
    assert payload["rationale"] == ["Improves academic word choice while preserving meaning."]
    assert "Risk: Main agent should confirm section-level framing." in payload["warnings"]
    assert "Question: Should the contribution sentence be more specific?" in payload["warnings"]
    assert payload["metadata"]["source"] == "specialist_suggestion"


def test_prepare_workbench_payload_rejects_invalid_suggestion(tmp_path):
    context_path, suggestion_path = build_valid_suggestion(tmp_path)
    payload_path = tmp_path / "workbench-payload.json"
    suggestion = json.loads(suggestion_path.read_text(encoding="utf-8"))
    suggestion["task_id"] = "wrong-task"
    suggestion_path.write_text(json.dumps(suggestion, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(
        ["python", str(SCRIPT), str(context_path), str(suggestion_path), str(payload_path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert not payload_path.exists()
    summary = json.loads(result.stdout)
    assert "task_id does not match task context" in summary["errors"]


def test_prepared_payload_builds_workbench_html(tmp_path):
    context_path, suggestion_path = build_valid_suggestion(tmp_path)
    payload_path = tmp_path / "workbench-payload.json"
    html_path = tmp_path / "workbench.html"

    subprocess.run(["python", str(SCRIPT), str(context_path), str(suggestion_path), str(payload_path)], check=True)
    subprocess.run(["python", str(WORKBENCH), str(payload_path), str(html_path)], check=True)

    html = html_path.read_text(encoding="utf-8")
    assert "Current Paragraph" in html
    assert "Prior work has examined" in html
    assert "Risk: Main agent should confirm section-level framing." in html
