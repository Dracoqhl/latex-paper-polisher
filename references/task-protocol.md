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
