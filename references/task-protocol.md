# Task Protocol

This document defines the model-led task plan and specialist-agent output schemas.

## Project Map Boundary

The project map is mechanical. It may describe files, anchors, labels, references, citations, captions, and protected regions. It must not decide which prose units should be polished.

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

Paper summaries are context artifacts and do not authorize source edits.

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

Generated suggestion templates leave `suggested_text` empty and list fields empty; they are intentionally invalid until the section specialist fills them. Validate section polish suggestions against the source package before merging them into a workbench-ready section polish package. Merging fills `suggested_text`, `revision_notes`, `risks`, and `questions`, but keeps `editable_text` equal to `original_text`.
For browser review, prefer the wrapper that validates suggestions, writes the merged package, and generates the section workbench HTML in one command so manual testing uses a single artifact chain.

## Section Final Edits

The section workbench downloads section-final-edits JSON after the user reviews the whole section.

Required fields:

```json
{
  "schema_version": 1,
  "mode": "section_final_edits",
  "section_id": "introduction",
  "section_title": "Introduction",
  "items": [
    {
      "item_id": "intro-p001",
      "source_file": "src/1_introduction.tex",
      "line_range": [10, 18],
      "original_text": "Original paragraph.",
      "final_text": "User-maintained final paragraph."
    }
  ]
}
```

Section final edits are staging artifacts. They do not modify source files. Before any later writeback preparation, validate section final edits against the source section polish package so item order, source locations, original text, and non-empty final text are confirmed.

## Section Writeback Candidate

A section writeback candidate is generated only after section final edits pass validation against the source section polish package.

Required fields:

```json
{
  "schema_version": 1,
  "mode": "section_writeback_candidate",
  "section_id": "introduction",
  "section_title": "Introduction",
  "source_file": "src/1_introduction.tex",
  "source_files": ["src/1_introduction.tex"],
  "items": [
    {
      "item_id": "intro-p001",
      "source_file": "src/1_introduction.tex",
      "line_range": [10, 18],
      "original_text": "Original paragraph.",
      "final_text": "User-maintained final paragraph."
    }
  ],
  "validation_required": true,
  "source_write_permitted": false,
  "metadata": {}
}
```

Section writeback candidates are staging artifacts. They do not modify source files and still require explicit writeback validation and user approval.

## Section Writeback Preflight

A section writeback preflight checks a section writeback candidate against a paper directory without modifying source files.

It verifies that each `original_text` appears exactly once in its target source file and compares LaTeX construct counts between `original_text` and `final_text`.

Preflight output contains:

```json
{
  "ok": true,
  "mode": "section_writeback_preflight",
  "section_id": "introduction",
  "project_root": "/path/to/paper",
  "source_write_permitted": false,
  "items": [],
  "errors": []
}
```

Passing preflight does not apply edits. It is evidence for a later explicitly approved writeback step.

## Section Writeback Dry Run

A section writeback dry run computes the source changes that would be applied from a preflight-passing section writeback candidate.

It produces a report with per-file unified diffs and never modifies source files:

```json
{
  "ok": true,
  "mode": "section_writeback_apply_dry_run",
  "section_id": "introduction",
  "dry_run": true,
  "source_write_permitted": false,
  "files": [
    {
      "source_file": "src/1_introduction.tex",
      "item_count": 2,
      "changed": true,
      "unified_diff": "--- a/src/1_introduction.tex\n+++ b/src/1_introduction.tex\n"
    }
  ],
  "errors": []
}
```

Dry-run reports are for review only. Actual source writeback requires a separate explicit command and user approval.

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

## Workbench Payload

A validated specialist suggestion may be converted into a workbench payload. The payload is the bridge between structured specialist output and the HTML workbench.

Workbench payloads contain:

```json
{
  "paragraph_id": "introduction-section-polish",
  "source_file": "src/1_introduction.tex",
  "section": "Polish Introduction",
  "original_text": "Original source text.",
  "suggested_text": "Suggested revision.",
  "rationale": ["Reason for the change."],
  "warnings": ["Risk: ...", "Question: ..."],
  "metadata": {}
}
```

The workbench remains review-only. Creating a payload or HTML page does not authorize source writeback.

## Workbench Review State

A workbench review-state payload merges the review-only text payload, the main-agent decision, and the writeback candidate status. It exists so the HTML workbench can show the current pipeline state and exact next CLI commands without directly modifying source files.

It may add these fields to the workbench payload:

```json
{
  "review_status": {
    "decision": "accept",
    "ready_for_writeback": true,
    "review_notes": "Main agent accepts specialist suggestion."
  },
  "writeback_candidate": {
    "available": true,
    "validation_required": true,
    "source_write_permitted": false,
    "line_range": [1, 30]
  },
  "next_commands": ["python scripts/prepare_writeback_candidate.py ..."]
}
```

The HTML page may display this state, but it must remain review-only until a later explicitly approved writeback step exists.

## Main-Agent Review Decision

After reviewing a workbench payload, the main agent records one explicit decision:

- `accept`: use the suggested text as the final candidate.
- `revise`: use a main-agent revised final text.
- `reject`: reject the suggestion and keep it out of writeback preparation.

Each decision record contains:

```json
{
  "schema_version": 1,
  "mode": "main_agent_review_decision",
  "paragraph_id": "introduction-section-polish",
  "source_file": "src/1_introduction.tex",
  "section": "Polish Introduction",
  "decision": "accept",
  "review_notes": "Main agent accepts specialist suggestion.",
  "original_text": "Original source text.",
  "suggested_text": "Suggested revision.",
  "final_text": "Final candidate text.",
  "ready_for_writeback": true,
  "metadata": {}
}
```

Only `accept` and `revise` decisions can become writeback candidates. A `reject` decision must keep `ready_for_writeback` false.

## Writeback Candidate

A writeback candidate is generated only from a main-agent review decision with `ready_for_writeback: true`. It packages the original source text and final candidate text for later validation and possible source writeback.

Each candidate contains:

```json
{
  "schema_version": 1,
  "mode": "writeback_candidate",
  "paragraph_id": "introduction-section-polish",
  "source_file": "src/1_introduction.tex",
  "section": "Polish Introduction",
  "decision": "accept",
  "original_text": "Original source text.",
  "final_text": "Final candidate text.",
  "line_range": [1, 30],
  "validation_required": true,
  "source_write_permitted": false,
  "metadata": {}
}
```

Writeback candidates do not modify source files. They are an explicit staging artifact for a later validation and writeback step.

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
