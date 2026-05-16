# Polishing Knowledge

This file is maintained automatically during paper polishing sessions. The user periodically reviews and corrects it.

## Confirmed Preferences

- Prefer academic English that is clear, precise, and not overstated.
- Maintain `architecture.md` alongside functional or file-structure changes. It is the source of truth for intended project layout and file placement rules.
- When future work updates files or functionality, update both the evolving knowledge base and `architecture.md` when their contents are affected.
- Python helpers should not own semantic paragraph splitting. They should provide source maps and validation only; the main agent should decompose polishing tasks after reading the paper.
- Specialist agents are suggestion-only by default. The main agent keeps exclusive writeback authority and reviews all suggestions before presenting final text to the user.
- Use `/data/latex_test` for manual external validation outputs when testing real LaTeX projects.
- Before polishing, generate a review bundle and inspect `task-review.md` / `task-board.json` so task scope can be reviewed, prioritized, skipped, or merged.
- Before generating section polish packages, create a paper-summary template from the project map, have the main agent fill the full-paper thesis/contributions/risks/section roles, and validate the completed summary.
- Generate section polish package templates from inspection data and the validated paper summary; template generation may carry paragraph/caption text and mechanical risks, but specialist agents fill the actual suggestions.
- Validate section-specialist suggestion JSON against the source section package before merging it into a workbench-ready package. Merging suggestions must not change the editable text default from original text.
- For HTML testing, prefer the one-command suggestions-to-workbench wrapper so validation, merge, and page generation stay in sync.
- Generate a per-task context package before asking a main agent or specialist agent to produce polishing suggestions.
- Generate and validate a specialist suggestion JSON before the main agent reviews or presents specialist output.
- Convert only validated specialist suggestions into workbench payloads; workbench HTML is still review-only and does not authorize writeback.
- Record the main agent's accept, revise, or reject decision before preparing any source writeback candidate.
- Writeback candidates are staging artifacts only. They require later validation and do not authorize source modification by themselves.
- First-version HTML integration should display review state and next CLI commands only; it must not directly modify source files.
- Reusable interactive workbench assets belong in the skill repository under `assets/workbench/`; paper-specific generated HTML and JSON belong in external runtime directories such as `/data/latex_test`.
- For the section workbench, the editable final-text box defaults to the original paragraph. Original and suggested panels should provide copy buttons, and all final edits are maintained manually by the user in the editable box.
- For section polishing, use one fresh specialist-agent context per section and reuse it for the whole section package; do not spawn a fresh agent per paragraph by default.
- Section polishing should use a precomputed section package so previous/next paragraph navigation is local and fast. The editable text defaults to original text, with original/suggested copy buttons for manual editing.
- Validate downloaded section-final-edits JSON against its source section package before preparing any writeback candidate.
- Section writeback candidates are still staging artifacts. They require later explicit validation and user approval before source files are modified.
- Run section writeback preflight before any source modification. Preflight must confirm exact single matches and LaTeX construct preservation, but it still does not authorize writeback by itself.
- Section writeback dry-run reports may show unified diffs for review, but dry-run mode must not modify paper source files.

## Section Rules

- See `section-style-rules.md` for defaults. Promote repeated user feedback here when it becomes a stable preference.

## Terminology

Record terms, abbreviations, method names, dataset names, variables, and phrases that must remain consistent.

## Common Errors

- Detect and replace Chinese punctuation, Chinese characters, and full-width symbols in English prose.
- Avoid unnecessary overclaiming.

## Scoped Notes

Use this section for paper-specific or chapter-specific requirements that should not yet become global preferences.
