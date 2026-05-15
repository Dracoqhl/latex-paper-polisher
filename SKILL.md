---
name: latex-paper-polisher
description: Use when polishing academic English papers in LaTeX projects, including macro-level reviewer-style structure analysis, paragraph-by-paragraph polishing with an HTML workbench, LaTeX-safe writeback, local logs, GitHub synchronization, and evolving polishing knowledge.
---

# latex-paper-polisher

## Purpose

Polish academic English LaTeX papers while preserving technical meaning and LaTeX source structure.

## Core Workflow

1. Inspect the current directory as a LaTeX project.
2. Use `scripts/inspect_latex_project.py` to build a mechanical index of files, sections, paragraphs, captions, labels, refs, citations, and math environments.
3. Read the indexed source context. Do not rely on the script alone for understanding.
4. Produce a detailed reviewer-style macro diagnosis before paragraph polishing:
   - section roles
   - argument chain
   - contribution framing
   - evidence and experiment support
   - section transitions
   - likely reviewer concerns
5. Confirm the macro optimization direction with the user.
6. Polish one natural paragraph or caption at a time.
7. Generate or refresh the current-paragraph HTML workbench with `scripts/build_workbench.py`.
8. Wait for the user's natural-language confirmation or revision request.
9. Write the confirmed final text back into the LaTeX source while preserving commands, citations, labels, refs, math, comments, and environments.
10. Validate the writeback with `scripts/validate_writeback.py` and by reviewing `git diff`.
11. Append a local-only log entry with `scripts/append_polish_log.py`.
12. Commit exactly that paragraph or caption change and push it to GitHub.
13. Update `references/knowledge.md` automatically when feedback reveals preferences, terminology, section rules, or common errors.
14. At chapter-level or full-pass milestones, ask whether to create and push a Git tag.

## Defaults

- Language: academic English only.
- Edit strength: medium polish. Preserve meaning while improving sentence structure, logical flow, and academic expression.
- Unit: natural paragraph split by blank lines.
- Figures and tables: polish captions or titles only, after reading surrounding context.
- HTML workbench: one persistent current-paragraph page. Completed paragraph history belongs in logs, not in the page.
- Logs: local only, not pushed to GitHub.
- Knowledge base: global skill references, updated automatically.

## Required Checks

- Detect Chinese characters, Chinese punctuation, and full-width symbols in English prose.
- Preserve LaTeX commands and technical meaning.
- Stop before committing if unrelated user changes are present.
- Keep logs out of GitHub.
- When files, directories, helper responsibilities, or workflow artifacts change, update `architecture.md`.
- When user preferences, terminology, recurring errors, or process preferences change, update `references/knowledge.md`.

## References

- Section-specific defaults: `references/section-style-rules.md`
- LaTeX preservation rules: `references/latex-preservation.md`
- Log format: `references/log-schema.md`
- Evolving knowledge: `references/knowledge.md`
- Project layout and file placement rules: `architecture.md`
