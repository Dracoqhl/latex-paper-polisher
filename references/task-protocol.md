# Task Protocol

This document defines the model-led task plan and specialist-agent output schemas.

## Project Map Boundary

The project map is mechanical. It may describe files, anchors, labels, references, citations, captions, and protected regions. It must not decide which prose units should be polished.

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
