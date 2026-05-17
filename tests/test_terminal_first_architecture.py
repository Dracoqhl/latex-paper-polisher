from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_html_workbench_workflow_files_are_removed():
    removed_paths = [
        "assets/workbench",
        "scripts/build_workbench.py",
        "scripts/build_section_workbench.py",
        "scripts/build_paper_overview.py",
        "scripts/prepare_workbench_payload.py",
        "scripts/prepare_workbench_review_state.py",
        "scripts/prepare_section_workbench_from_suggestions.py",
        "scripts/record_review_decision.py",
        "scripts/prepare_writeback_candidate.py",
        "scripts/validate_section_final_edits.py",
        "scripts/prepare_section_writeback_candidate.py",
        "scripts/preflight_section_writeback.py",
        "scripts/apply_section_writeback_candidate.py",
    ]

    existing_paths = [path for path in removed_paths if (ROOT / path).exists()]

    assert existing_paths == []


def test_primary_skill_is_terminal_first():
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "Terminal-first" in skill_text
    assert "HTML workbench" not in skill_text
