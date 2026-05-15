# Project Architecture

This document defines the intended project layout and file placement rules.

Update this file whenever a change adds, removes, renames, or materially changes the responsibility of a file, directory, helper script, reference document, test fixture, or workflow artifact.

## Root Files

- `SKILL.md`: Codex skill instructions, trigger conditions, workflow order, agent responsibilities, and safety requirements.
- `architecture.md`: Project layout, file placement rules, and ownership boundaries. Keep this synchronized with functional and structural changes.
- `.gitignore`: Local-only artifacts, Python caches, generated logs, and temporary files that must not be committed.

## Agent Metadata

- `agents/openai.yaml`: Skill display metadata and default prompt text for OpenAI/Codex environments.

## Helper Scripts

All executable helper scripts live under `scripts/`.

- `scripts/inspect_latex_project.py`: Mechanical LaTeX project inspection. It may discover files, sections, paragraphs, captions, labels, refs, citations, and math spans, but it must not be treated as the semantic authority for polishing units.
- `scripts/build_workbench.py`: Static HTML workbench generation for the current paragraph or scoped text unit.
- `scripts/append_polish_log.py`: Append-only local JSONL log writer for completed polishing actions.
- `scripts/validate_writeback.py`: Before/after LaTeX construct safety checker for source writeback.

Future scripts should stay small and deterministic. If a script starts making writing-quality, paper-structure, or polishing-priority decisions, move that responsibility back to the main agent workflow and document the boundary here.

## References

Reference material lives under `references/`.

- `references/knowledge.md`: Evolving user preferences, terminology, common errors, and scoped notes learned during polishing sessions.
- `references/section-style-rules.md`: Default academic writing conventions by paper section.
- `references/latex-preservation.md`: Rules for preserving LaTeX constructs during review and writeback.
- `references/log-schema.md`: Local polish log schema and storage policy.

When user preferences or recurring project rules change, update `references/knowledge.md`. When file placement or responsibilities change, update this document as well.

## Design And Plans

Superpowers design and implementation planning documents live under `docs/superpowers/`.

- `docs/superpowers/specs/`: Approved or proposed design documents.
- `docs/superpowers/plans/`: Implementation plans derived from design documents.

Do not place runtime state, generated workbench pages, or polishing logs under `docs/`.

## Tests And Fixtures

Tests live under `tests/`.

- `tests/test_*.py`: Pytest test files for helper scripts and workflow behavior.
- `tests/fixtures/`: Small committed fixtures used for deterministic tests.

Large real paper projects must not be copied into this repository as fixtures. Use external paper directories read-only and write generated validation output to `/tmp` or another ignored location.

## Local-Only Runtime Artifacts

Runtime artifacts must not be committed.

- `.latex-paper-polisher/logs/`: Local polishing logs.
- `.pytest_cache/`: Pytest cache.
- `__pycache__/` and `*.pyc`: Python bytecode cache.
- Generated workbench HTML for real polishing sessions unless a test explicitly creates it under a temporary directory.

## File Placement Rules

- Put deterministic tooling in `scripts/`.
- Put skill instructions in `SKILL.md`.
- Put stable reference policy in `references/`.
- Put design decisions and future implementation plans in `docs/superpowers/`.
- Put committed test inputs in `tests/fixtures/`.
- Put generated, local, or paper-specific runtime output outside the repository or in ignored directories.
- Keep source writeback authority in the main agent workflow; helper scripts may validate or format data, but they should not make semantic polishing decisions.
