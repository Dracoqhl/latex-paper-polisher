# Project Architecture

This document defines the intended project layout and file placement rules.

Update this file whenever a change adds, removes, renames, or materially changes the responsibility of a file, directory, helper script, reference document, test fixture, or workflow artifact.

## Root Files

- `SKILL.md`: Codex skill instructions, trigger conditions, workflow order, agent responsibilities, and safety requirements.
- `architecture.md`: Project layout, file placement rules, and ownership boundaries. Keep this synchronized with functional and structural changes.
- `.gitignore`: Local-only artifacts, Python caches, generated logs, and temporary files that must not be committed.

## Agent Metadata

- `agents/openai.yaml`: Skill display metadata and default prompt text for OpenAI/Codex environments.

## User Interaction Model

The active polishing workflow is Terminal-first. Codex reads LaTeX source and surrounding context, discusses section or paragraph revisions with the user in the terminal, and edits source files only after explicit user confirmation.

Browser HTML workbench assets and generators are intentionally not part of the active architecture. Historical HTML plans remain in `docs/superpowers/` only as project history.

## Helper Scripts

All executable helper scripts live under `scripts/`.

- `scripts/inspect_latex_project.py`: Mechanical LaTeX project inspection and `--map` project-map generation. It may discover files, sections, paragraphs, captions, labels, refs, citations, and math spans, but it must not be treated as the semantic authority for polishing units.
- `scripts/check_paper_git.py`: Read-only paper repository guard. It reports whether a target paper directory is a git repository, the repository root, current branch, and dirty files before any direct source edit.
- `scripts/build_task_skeleton.py`: Generates a mechanical starter task skeleton from a project map. The skeleton requires main-agent review before use.
- `scripts/prepare_review_bundle.py`: Generates project map, task skeleton, task board, review Markdown, and read-only summary for human task-decomposition review.
- `scripts/prepare_paper_summary_template.py`: Generates a fillable paper-summary template from a mechanical project map after the main agent has inspected the full-paper structure.
- `scripts/validate_paper_summary.py`: Validates a completed paper-summary JSON before it is used as context for section polish packages.
- `scripts/prepare_section_polish_package_template.py`: Generates a fillable section polish package template from full inspection data and a validated paper summary for one target section.
- `scripts/prepare_task_context.py`: Generates per-task JSON and Markdown context packages from a reviewed task board for main-agent or specialist-agent review.
- `scripts/prepare_suggestion_template.py`: Generates a structured specialist-suggestion JSON template from one task context package.
- `scripts/validate_specialist_suggestion.py`: Validates a specialist-suggestion JSON file against the task context before the main agent reviews or presents it.
- `scripts/prepare_section_polish_suggestions_template.py`: Generates a fillable section-specialist suggestions template from a section polish package.
- `scripts/validate_section_polish_suggestions.py`: Validates section-specialist suggestion JSON against its source section package before merge.
- `scripts/merge_section_polish_suggestions.py`: Merges validated section-specialist suggestions into a section polish package while preserving original editable text defaults.
- `scripts/validate_section_polish_package.py`: Validates section polish package JSON for optional section-specialist suggestion workflows.
- `scripts/run_readonly_real_paper_check.py`: Runs the mapper and task skeleton builder against an external LaTeX project, writes outputs to a chosen test directory, and verifies the source project was not modified.
- `scripts/append_polish_log.py`: Append-only local JSONL log writer for completed polishing actions.
- `scripts/record_terminal_polish_session.py`: Append-only terminal polishing session logger. It records confirmed semantic-unit edits with excerpt hashes, validation summaries, paper commit hashes, and knowledge updates.
- `scripts/validate_writeback.py`: Before/after LaTeX construct safety checker for source writeback.

Future scripts should stay small and deterministic. If a script starts making writing-quality, paper-structure, polishing-priority, or source-edit decisions, move that responsibility back to the main agent workflow and document the boundary here.

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

Do not place runtime state, generated review artifacts, or polishing logs under `docs/`.
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
- Manual real-paper validation outputs under `/data/latex_test/`.
- Review-bundle outputs under `/data/latex_test/`: `project-map.json`, `task-skeleton.json`, `task-board.json`, `task-review.md`, and `readonly-summary.json`.
- Per-task context packages under `/data/latex_test/` or a subdirectory of it.
- Specialist suggestion templates and returned suggestion JSON files under `/data/latex_test/` or a subdirectory of it.
- Paper summary templates, completed paper summaries, section polish package templates, section-specialist suggestion JSON, and merged section polish packages under `/data/latex_test/` or another runtime output directory.
- Paper-specific local logs under the paper project or another ignored runtime directory.

## File Placement Rules

- Put deterministic tooling in `scripts/`.
- Put skill instructions in `SKILL.md`.
- Put stable reference policy in `references/`.
- Put shared task and agent-output protocols in `references/`, not in scripts.
- Put design decisions and future implementation plans in `docs/superpowers/`.
- Put committed test inputs in `tests/fixtures/`.
- Put generated, local, or paper-specific runtime output outside the repository or in ignored directories.
- Put manual external validation outputs in `/data/latex_test/` when the directory is available.
- Keep source writeback authority in the main agent workflow; helper scripts may validate or format data, but they should not make semantic polishing decisions or apply source edits.
- Manage paper-source edits in each paper project's own git repository. Manage tool, documentation, and test changes in this repository.
- Run `scripts/check_paper_git.py` against a paper project before direct source edits. If the target is not a git repository, initialize git only after explicit user approval. If unrelated dirty files are present, stop and ask how to proceed.
