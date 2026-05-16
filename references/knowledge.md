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
- Generate a per-task context package before asking a main agent or specialist agent to produce polishing suggestions.
- Generate and validate a specialist suggestion JSON before the main agent reviews or presents specialist output.
- Convert only validated specialist suggestions into workbench payloads; workbench HTML is still review-only and does not authorize writeback.
- Record the main agent's accept, revise, or reject decision before preparing any source writeback candidate.
- Writeback candidates are staging artifacts only. They require later validation and do not authorize source modification by themselves.
- First-version HTML integration should display review state and next CLI commands only; it must not directly modify source files.

## Section Rules

- See `section-style-rules.md` for defaults. Promote repeated user feedback here when it becomes a stable preference.

## Terminology

Record terms, abbreviations, method names, dataset names, variables, and phrases that must remain consistent.

## Common Errors

- Detect and replace Chinese punctuation, Chinese characters, and full-width symbols in English prose.
- Avoid unnecessary overclaiming.

## Scoped Notes

Use this section for paper-specific or chapter-specific requirements that should not yet become global preferences.
