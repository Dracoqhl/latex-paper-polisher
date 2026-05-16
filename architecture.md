# Project Architecture

This document defines the intended project layout and file placement rules.

Update this file whenever a change adds, removes, renames, or materially changes the responsibility of a file, directory, helper script, reference document, test fixture, or workflow artifact.

## Root Files

- `SKILL.md`: Codex skill instructions, trigger conditions, workflow order, agent responsibilities, and safety requirements.
- `architecture.md`: Project layout, file placement rules, and ownership boundaries. Keep this synchronized with functional and structural changes.
- `.gitignore`: Local-only artifacts, Python caches, generated logs, and temporary files that must not be committed.

## Agent Metadata

- `agents/openai.yaml`: Skill display metadata and default prompt text for OpenAI/Codex environments.

## Workbench Assets

Reusable browser workbench assets live under `assets/workbench/`.

- `assets/workbench/workbench.html`: HTML template used by `scripts/build_workbench.py`.
- `assets/workbench/workbench.css`: Shared workbench styling.
- `assets/workbench/workbench.js`: Browser-side review decision controls. It generates decision JSON for the user to inspect or download, but it does not write source files.

## Helper Scripts

All executable helper scripts live under `scripts/`.

- `scripts/inspect_latex_project.py`: Mechanical LaTeX project inspection and `--map` project-map generation. It may discover files, sections, paragraphs, captions, labels, refs, citations, and math spans, but it must not be treated as the semantic authority for polishing units.
- `scripts/build_task_skeleton.py`: Generates a mechanical starter task skeleton from a project map. The skeleton requires main-agent review before use.
- `scripts/prepare_review_bundle.py`: Generates project map, task skeleton, task board, review Markdown, and read-only summary for human task-decomposition review.
- `scripts/prepare_task_context.py`: Generates per-task JSON and Markdown context packages from a reviewed task board for main-agent or specialist-agent review.
- `scripts/prepare_suggestion_template.py`: Generates a structured specialist-suggestion JSON template from one task context package.
- `scripts/validate_specialist_suggestion.py`: Validates a specialist-suggestion JSON file against the task context before the main agent reviews or presents it.
- `scripts/prepare_workbench_payload.py`: Converts a validated specialist suggestion into the JSON payload consumed by the HTML workbench generator.
- `scripts/prepare_workbench_review_state.py`: Merges a workbench payload, main-agent review decision, and writeback candidate into an HTML-ready review-state payload.
- `scripts/record_review_decision.py`: Records the main agent's accept, revise, or reject decision for a workbench payload and marks whether it is ready for writeback.
- `scripts/prepare_writeback_candidate.py`: Converts an accepted or revised main-agent review decision into a writeback candidate JSON without modifying source files.
- `scripts/validate_section_polish_package.py`: Validates section polish package JSON before generating a section workbench.
- `scripts/build_section_workbench.py`: Generates an interactive section-level HTML workbench from a section polish package.
- `scripts/validate_section_final_edits.py`: Validates downloaded section-final-edits JSON against its source section polish package before any later writeback preparation.
- `scripts/run_readonly_real_paper_check.py`: Runs the mapper and task skeleton builder against an external LaTeX project, writes outputs to a chosen test directory, and verifies the source project was not modified.
- `scripts/build_workbench.py`: Static HTML workbench generation for the current paragraph or scoped text unit. It reads reusable assets from `assets/workbench/`, embeds the current payload, and includes optional review status and next-command sections.
- `scripts/append_polish_log.py`: Append-only local JSONL log writer for completed polishing actions.
- `scripts/validate_writeback.py`: Before/after LaTeX construct safety checker for source writeback.

Future scripts should stay small and deterministic. If a script starts making writing-quality, paper-structure, or polishing-priority decisions, move that responsibility back to the main agent workflow and document the boundary here.

## References

Reference material lives under `references/`.

- `references/knowledge.md`: Evolving user preferences, terminology, common errors, and scoped notes learned during polishing sessions.
- `references/section-style-rules.md`: Default academic writing conventions by paper section.
- `references/latex-preservation.md`: Rules for preserving LaTeX constructs during review and writeback.
- `references/log-schema.md`: Local polish log schema and storage policy.
- `references/task-protocol.md`: Task plan and specialist-agent output schemas for model-led decomposition.

When user preferences or recurring project rules change, update `references/knowledge.md`. When file placement or responsibilities change, update this document as well.

## Design And Plans

Superpowers design and implementation planning documents live under `docs/superpowers/`.

- `docs/superpowers/specs/`: Approved or proposed design documents.
- `docs/superpowers/plans/`: Implementation plans derived from design documents.

Do not place runtime state, generated workbench pages, or polishing logs under `docs/`.
Current Phase 2 planning is tracked in `docs/superpowers/plans/2026-05-15-model-led-task-decomposition.md`.

## Tests And Fixtures

Tests live under `tests/`.

- `tests/test_*.py`: Pytest test files for helper scripts and workflow behavior.
- `tests/fixtures/`: Small committed fixtures used for deterministic tests.

Large real paper projects must not be copied into this repository as fixtures. Use external paper directories read-only and write generated validation output to `/tmp` or another ignored location.
For user-facing manual validation, prefer `/data/latex_test` as the external output directory.

## Local-Only Runtime Artifacts

Runtime artifacts must not be committed.

- `.latex-paper-polisher/logs/`: Local polishing logs.
- `.pytest_cache/`: Pytest cache.
- `.superpowers/`: Local visual brainstorming companion state and mockups.
- `__pycache__/` and `*.pyc`: Python bytecode cache.
- Generated workbench HTML for real polishing sessions unless a test explicitly creates it under a temporary directory.
- Manual real-paper validation outputs under `/data/latex_test/`.
- Review-bundle outputs under `/data/latex_test/`: `project-map.json`, `task-skeleton.json`, `task-board.json`, `task-review.md`, and `readonly-summary.json`.
- Per-task context packages under `/data/latex_test/` or a subdirectory of it.
- Specialist suggestion templates and returned suggestion JSON files under `/data/latex_test/` or a subdirectory of it.
- Workbench payload JSON and generated HTML under `/data/latex_test/` or a subdirectory of it for manual validation.
- Main-agent review decision JSON under `/data/latex_test/` or a subdirectory of it for manual validation.
- Writeback candidate JSON under `/data/latex_test/` or a subdirectory of it for manual validation.
- Workbench review-state payload JSON under `/data/latex_test/` or a subdirectory of it for manual validation.
- Paper summary, section polish package, section final edits, and generated section workbench HTML under `/data/latex_test/` or another runtime output directory.

## File Placement Rules

- Put deterministic tooling in `scripts/`.
- Put skill instructions in `SKILL.md`.
- Put stable reference policy in `references/`.
- Put shared task and agent-output protocols in `references/`, not in scripts.
- Put design decisions and future implementation plans in `docs/superpowers/`.
- Put committed test inputs in `tests/fixtures/`.
- Put reusable workbench HTML/CSS/JS in `assets/workbench/`; put generated paper-specific workbench output outside the repository.
- Put generated, local, or paper-specific runtime output outside the repository or in ignored directories.
- Put manual external validation outputs in `/data/latex_test/` when the directory is available.
- Keep source writeback authority in the main agent workflow; helper scripts may validate or format data, but they should not make semantic polishing decisions.
