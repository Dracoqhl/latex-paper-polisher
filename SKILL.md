---
name: latex-paper-polisher
description: Use when polishing academic English papers in LaTeX projects, including macro-level reviewer-style structure analysis, paragraph-by-paragraph polishing with an HTML workbench, LaTeX-safe writeback, local logs, GitHub synchronization, and evolving polishing knowledge.
---

# latex-paper-polisher

## Purpose

Polish academic English LaTeX papers while preserving technical meaning and LaTeX source structure.

## Core Workflow

1. Inspect the current directory as a LaTeX project.
2. Use `scripts/inspect_latex_project.py --map` to build a mechanical project map.
3. Treat the map as source navigation only. Python must not decide polishing units.
4. Main agent reads the main file, section files, references, and relevant project context.
5. Main agent produces a paper-level task plan organized by macro review, section polishing, captions, terminology, CJK/full-width scan, and LaTeX safety checks.
6. Confirm the task order and macro optimization direction with the user.
7. Optionally dispatch specialist agents for scoped suggestions. Specialist agents must not edit files, commit, push, or update logs.
8. Main agent reviews specialist suggestions for paper consistency, terminology, LaTeX preservation, and user preferences.
9. Generate or refresh the HTML workbench when a specific text unit is ready for user review.
10. Wait for the user's natural-language confirmation or revision request.
11. Main agent performs the only writeback to LaTeX source after user confirmation.
12. Validate the writeback with `scripts/validate_writeback.py` and by reviewing `git diff`.
13. Append a local-only log entry with `scripts/append_polish_log.py`.
14. Commit exactly the confirmed source change and push it to GitHub.
15. Update `references/knowledge.md` and `architecture.md` when their contents are affected.

## Defaults

- Language: academic English only.
- Edit strength: medium polish. Preserve meaning while improving sentence structure, logical flow, and academic expression.
- Unit: natural paragraph split by blank lines.
- Task decomposition: model-led by the main agent after reading project context.
- Helper scripts: mechanical source mapping, workbench generation, logging, and validation only.
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
- Task and specialist-agent protocol: `references/task-protocol.md`
- Evolving knowledge: `references/knowledge.md`
- Project layout and file placement rules: `architecture.md`
