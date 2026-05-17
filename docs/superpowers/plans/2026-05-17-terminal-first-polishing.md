# Terminal-First Polishing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the browser workbench workflow with a terminal-native polishing workflow where Codex analyzes sections, discusses revisions with the user, directly edits confirmed LaTeX source, validates, and commits in the paper repository.

**Architecture:** The tool repository provides deterministic helpers for project inspection, context packaging, suggestion validation, logs, and LaTeX safety checks. The main agent owns semantic decomposition, writing judgment, user discussion, source edits, and git commits in each paper project. HTML workbench assets and browser review payloads are not part of the active architecture.

**Tech Stack:** Markdown skill/reference docs, Python 3 standard-library helper scripts, pytest tests, git.

---

## Task 1: Remove Browser Workbench Workflow

**Files:**
- Delete: `assets/workbench/`
- Delete: `scripts/build_workbench.py`
- Delete: `scripts/build_section_workbench.py`
- Delete: `scripts/build_paper_overview.py`
- Delete: `scripts/prepare_workbench_payload.py`
- Delete: `scripts/prepare_workbench_review_state.py`
- Delete: `scripts/prepare_section_workbench_from_suggestions.py`
- Delete: `scripts/record_review_decision.py`
- Delete: `scripts/prepare_writeback_candidate.py`
- Delete: `scripts/validate_section_final_edits.py`
- Delete: `scripts/prepare_section_writeback_candidate.py`
- Delete: `scripts/preflight_section_writeback.py`
- Delete: `scripts/apply_section_writeback_candidate.py`
- Delete matching tests for those scripts.
- Modify: `tests/test_smoke_workflow.py`
- Create: `tests/test_terminal_first_architecture.py`

- [x] **Step 1: Add failing architecture test**

Add `tests/test_terminal_first_architecture.py` to assert the removed browser workflow files are absent and `SKILL.md` declares Terminal-first behavior.

- [x] **Step 2: Run architecture test to verify red**

Run: `pytest tests/test_terminal_first_architecture.py -q`

Expected: FAIL while old HTML assets/scripts and old skill text still exist.

- [x] **Step 3: Delete browser workflow files and tests**

Remove the HTML assets, HTML builders, browser payload scripts, browser review-state scripts, staged writeback scripts that only existed for the HTML flow, and their tests.

- [x] **Step 4: Update smoke workflow**

Change smoke coverage from `inspect -> workbench -> log -> validation` to `inspect -> validate_writeback -> log`.

## Task 2: Update Active Workflow Documentation

**Files:**
- Modify: `SKILL.md`
- Modify: `agents/openai.yaml`
- Modify: `architecture.md`
- Modify: `references/knowledge.md`
- Modify: `references/task-protocol.md`

- [x] **Step 1: Update skill instructions**

Make Terminal-first polishing the default workflow: inspect, read context, analyze section/paragraph purposes, discuss wording, directly edit confirmed source, validate, log, and commit locally in the paper repository.

- [x] **Step 2: Update architecture**

Document that browser workbench assets are intentionally removed from active architecture. Define the git boundary: paper repositories own paper-source commits; this repository owns tools, docs, tests, and skill behavior.

- [x] **Step 3: Update knowledge and task protocol**

Record the user preference for terminal-native collaboration and remove active browser-review protocol sections from `references/task-protocol.md`.

## Task 3: Build Paper-Repository Git Guard

**Files:**
- Create: `scripts/check_paper_git.py`
- Create: `tests/test_check_paper_git.py`
- Modify: `architecture.md`
- Modify: `references/task-protocol.md`

- [x] **Step 1: Write failing tests**

Test that `scripts/check_paper_git.py PAPER_ROOT` reports:

```json
{
  "ok": true,
  "is_git_repo": true,
  "branch": "main",
  "dirty_files": []
}
```

for a clean fixture git repository, and returns `ok: false` when the target directory is not a git repository.

- [x] **Step 2: Implement git guard**

Use non-destructive `git -C PAPER_ROOT status --short`, `git -C PAPER_ROOT branch --show-current`, and `git -C PAPER_ROOT rev-parse --show-toplevel`. Do not initialize git automatically unless the user explicitly asks.

- [x] **Step 3: Document usage**

Before direct source edits, run the guard. If the paper repo has unrelated dirty files, stop and ask the user how to proceed.

- [x] **Step 4: Verify and commit**

Run `pytest tests/test_check_paper_git.py -q`, then full `pytest -q`, then commit in the tool repository.

## Task 4: Add Terminal Polishing Session Log Helper

**Files:**
- Create: `scripts/record_terminal_polish_session.py`
- Create: `tests/test_record_terminal_polish_session.py`
- Modify: `references/log-schema.md`
- Modify: `architecture.md`

- [x] **Step 1: Write failing tests**

Test that the helper records target section, source files touched, original excerpt hash, final excerpt hash, validation command summary, paper commit hash, and user preference updates.

- [x] **Step 2: Implement append-only session logging**

Write JSONL under a caller-provided path, usually inside an ignored paper-local log directory. The helper must not edit source files or commit.

- [x] **Step 3: Verify and commit**

Run targeted tests, full tests, and commit.

## Task 5: Add Direct-Edit Safety Checklist

**Files:**
- Create: `references/terminal-polishing-workflow.md`
- Modify: `SKILL.md`
- Modify: `architecture.md`

- [x] **Step 1: Write workflow reference**

Document the direct-edit loop:

1. Confirm paper repo git status.
2. Read section context.
3. Provide paragraph-purpose analysis.
4. Discuss one semantic unit.
5. Apply confirmed source edit.
6. Run LaTeX construct validation and inspect diff.
7. Commit in the paper repo.
8. Update knowledge when preferences change.

- [x] **Step 2: Link from `SKILL.md`**

Add the new workflow reference to the skill references.

- [x] **Step 3: Verify and commit**

Run docs grep checks and full tests, then commit.
