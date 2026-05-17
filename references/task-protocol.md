# Task Protocol

This document defines the model-led task plan and specialist-agent output schemas.

## Project Map Boundary

The project map is mechanical. It may describe files, anchors, labels, references, citations, captions, and protected regions. It must not decide which prose units should be polished.

## Paper Git Guard

Before directly editing a paper source file, run:

```bash
python scripts/check_paper_git.py /path/to/paper
```

The guard is read-only. It reports whether the paper directory is a git repository, the repository root, current branch, and dirty files:

```json
{
  "ok": true,
  "is_git_repo": true,
  "repo_root": "/path/to/paper",
  "branch": "main",
  "dirty_files": [],
  "errors": []
}
```

If `is_git_repo` is false, ask the user before initializing git. If `dirty_files` contains unrelated changes, stop and ask the user whether to commit, ignore, or review those changes before polishing.

## Paper Summary

A paper summary is generated after the main agent reads the full paper. It captures paper-level understanding for later section specialist agents.

Required fields:

```json
{
  "schema_version": 1,
  "mode": "paper_summary",
  "project_root": "/path/to/paper",
  "main_file": "main.tex",
  "thesis": "Main paper claim.",
  "contributions": [],
  "section_map": [],
  "terminology": [],
  "macro_risks": [],
  "structural_suggestions": [],
  "polishing_guidance": []
}
```

Generate the initial paper summary template from a project map, then have the main agent fill it after reading the full paper. Validate the completed summary before any section specialist uses it as context.

Paper summaries are context artifacts and do not authorize source edits. Use them as terminal discussion context when the user asks to improve a section or paper-level framing.

## Section Polish Package

A section polish package starts as a deterministic template generated from full inspection data plus a validated paper summary for one target section. One fresh section-specialist agent context then reads that template, the full section, the paper summary, and any needed neighboring context before filling suggestions.

Required fields:

```json
{
  "schema_version": 1,
  "mode": "section_polish_package",
  "section_id": "introduction",
  "section_title": "Introduction",
  "source_file": "src/1_introduction.tex",
  "paper_summary_ref": "paper-summary.json",
  "items": [
    {
      "item_id": "intro-p001",
      "source_file": "src/1_introduction.tex",
      "line_range": [10, 18],
      "original_text": "Original paragraph.",
      "suggested_text": "Suggested revision.",
      "revision_notes": ["Why this change helps."],
      "risks": [],
      "questions": [],
      "editable_text": "Original paragraph."
    }
  ]
}
```

`editable_text` must default to `original_text`. Template generation leaves `suggested_text`, `revision_notes`, and `questions` empty for the section specialist to fill. The suggested text is not automatically adopted.

## Section Polish Suggestions

A section polish suggestion file starts as a deterministic template generated from a source section polish package. It is then returned by one fresh section-specialist agent after it reads the template, section polish package, paper summary, and any needed neighboring context. It is suggestion-only and must match the source package item ids, source locations, and original text exactly.

Required fields:

```json
{
  "schema_version": 1,
  "mode": "section_polish_suggestions",
  "section_id": "introduction",
  "section_title": "Introduction",
  "source_package_ref": "section-polish-package-introduction-template.json",
  "items": [
    {
      "item_id": "intro-p001",
      "source_file": "src/1_introduction.tex",
      "line_range": [10, 18],
      "original_text": "Original paragraph.",
      "suggested_text": "Suggested revision.",
      "revision_notes": ["Why this change helps."],
      "risks": [],
      "questions": []
    }
  ]
}
```

Generated suggestion templates leave `suggested_text` empty and list fields empty; they are intentionally invalid until the section specialist fills them. Validate section polish suggestions against the source package before using them in terminal discussion. Merging fills `suggested_text`, `revision_notes`, `risks`, and `questions`, but keeps `editable_text` equal to `original_text`.

## Main-Agent Task Plan

The main agent creates and owns the task plan after reading the paper context.

Each task is a JSON object with:

```json
{
  "id": "introduction-section-polish",
  "type": "section_polish",
  "title": "Polish Introduction",
  "target_files": ["src/1_introduction.tex"],
  "anchors": [{"file": "src/1_introduction.tex", "line": 1, "kind": "section", "title": "Introduction"}],
  "status": "pending",
  "assigned_role": "section_polisher",
  "required_context": ["paper thesis", "section role", "terminology", "latex preservation rules"],
  "acceptance_check": "User approves final wording and validator reports no LaTeX construct damage."
}
```

Valid task types:

- `macro_review`
- `section_polish`
- `caption_polish`
- `terminology_check`
- `latex_safety_check`
- `cjk_fullwidth_scan`

Valid statuses:

- `pending`
- `in_progress`
- `blocked`
- `review_ready`
- `user_approved`
- `completed`

## Specialist-Agent Output

Specialist agents return suggestions only. They must not edit files, commit, push, or update logs.

Each output is a JSON object with:

```json
{
  "task_id": "introduction-section-polish",
  "target": {"file": "src/1_introduction.tex", "line_range": [1, 30]},
  "original_text": "Original source excerpt.",
  "proposed_text": "Suggested revision.",
  "rationale": ["Reason for the change."],
  "latex_constructs_preserved": ["\\\\citep{...}", "Figure~\\\\ref{fig:...}"],
  "risks": [],
  "questions": []
}
```

The main agent reviews specialist output before presenting final text to the user.

## Specialist Suggestion Handoff

Before asking a specialist agent for polishing suggestions, generate a suggestion template from the task context package. The template fixes the task id, target file, source line range, original text, and suggestion-only metadata.

Specialist agents fill only these review fields:

- `proposed_text`
- `rationale`
- `latex_constructs_preserved`
- `risks`
- `questions`

After receiving a suggestion, validate it against the task context. Validation only checks schema and source-boundary consistency; it does not decide whether the prose is good enough. The main agent must still review meaning, terminology, paper-level consistency, and LaTeX preservation before presenting text to the user.

## Terminal Revision Confirmation

For the active Terminal-first workflow, no browser payload or staged writeback candidate is required. The main agent presents analysis and proposed wording in the terminal, discusses revisions with the user, and edits source only after the user confirms the final text.

The confirmation record lives in the conversation and, when useful, in the local polishing log. The paper project's git commit is the durable source-edit record.

## Task Board

The task board is the main-agent review layer over the mechanical task skeleton. It preserves every skeleton task and adds review fields:

```json
{
  "priority": "normal",
  "phase": "section",
  "review_decision": "unreviewed",
  "user_notes": [],
  "main_agent_notes": []
}
```

Valid `phase` values:

- `global`
- `section`
- `caption`

Initial `review_decision` is `unreviewed`. During task review, the user or main agent may mark tasks as `keep`, `skip`, `merge`, or `prioritize`.

## Task Context Package

A task context package is generated from a task board for one task. It is intended for main-agent review or specialist-agent suggestion generation.

Each package contains:

```json
{
  "schema_version": 1,
  "mode": "task_context_package",
  "project_root": "/path/to/paper",
  "main_file": "main.tex",
  "task": {},
  "source_contexts": [
    {
      "file": "src/1_introduction.tex",
      "line_start": 1,
      "line_end": 30,
      "text": "LaTeX source text"
    }
  ],
  "instructions": []
}
```

Task context packages are read-only review inputs. They must not be treated as authorization to write back to the source paper.
