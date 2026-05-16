# Section Workbench Design

## Purpose

The polishing workflow should move from per-paragraph model calls to a section-level review workflow. The main agent first builds a paper-level understanding, then a section agent produces a local package of paragraph-level suggestions for one section. The browser workbench then lets the user review, edit, and submit the whole section without repeatedly waiting for model calls while moving between paragraphs.

## Confirmed User Requirements

- The user specifies a LaTeX paper directory.
- Before section polishing, the main agent reads the full paper and produces a macro-level understanding.
- The macro-level summary must be available to later section and paragraph polishing agents.
- During section polishing, an agent reads the whole section and, when needed, adjacent context or other relevant paragraphs.
- The section agent generates all paragraph-level suggestions for the section in one local package.
- The HTML workbench navigates locally through precomputed section items, so previous/next paragraph movement is fast.
- The editable final-text box defaults to the original paragraph, not the suggested version.
- The original and suggested text panels each have a copy button.
- The user manually maintains the editable final text. All final edits are based on that field.
- The page includes a conversation area for discussing the current paragraph with a polishing agent.
- The first implementation stores edits in browser memory and downloads a section-final-edits JSON when the user submits the whole section.
- The first implementation does not directly modify paper source files.

## Workflow

### 1. Paper Summary

After receiving a paper directory, the main agent reads the project map and relevant source files, then writes a local paper summary artifact:

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

This summary is a context artifact. It does not authorize source edits.

### 2. Section Polish Package

For one selected section, the agent reads:

- the paper summary
- the full section source
- relevant neighboring section context when needed
- LaTeX preservation rules and user preferences

It writes a local section package:

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

`editable_text` defaults to `original_text`. The suggested version is available for copying, but it is not automatically adopted.

### 3. Section Workbench

The browser workbench loads one section package and displays a local section browser:

- top status: section title, current item index, source file, line range
- current paragraph area:
  - left panel: original text with copy button
  - right panel: suggested text with copy button
- revision notes list
- risks and questions, if present
- editable final-text textarea, defaulting to the current item's `editable_text`
- previous and next paragraph buttons
- polishing-agent discussion area
- submit whole section button

When the user changes paragraphs, the page saves the current textarea value into browser memory and then loads the next item. No model call is required for previous/next navigation.

### 4. Section Final Edits

When the user clicks submit whole section, the browser downloads:

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

This is still a staging artifact. A later writeback step must validate and apply edits explicitly.

## Workbench Interaction Rules

- Previous/next navigation must not call a model.
- Copy buttons only copy text to the clipboard; they do not change the editable final text.
- The final-text textarea is the only source of truth for the user's final paragraph version.
- Agent discussion output must not overwrite final text automatically.
- Submit whole section downloads JSON only in the first version.
- Generated HTML and runtime JSON stay outside the skill repository, typically under `/data/latex_test`.

## Implementation Boundaries

Reusable workbench assets belong in `assets/workbench/`.

Generated paper-specific artifacts belong in external runtime directories:

- `paper-summary.json`
- `section-polish-package-<section-id>.json`
- `section-final-edits-<section-id>.json`
- generated HTML files

The initial implementation should not introduce a local backend. Browser memory plus downloaded JSON is sufficient for the first usable section workbench.

## Testing Strategy

- Unit-test paper summary and section package schema generation.
- Unit-test section workbench HTML generation from a fixture section package.
- Browser-independent tests should assert that HTML contains previous/next controls, copy buttons, editable final text, discussion area, and submit-section behavior.
- Manual validation should generate a sample workbench under `/data/latex_test` and serve it through the existing static server.
