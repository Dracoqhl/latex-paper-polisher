---
name: latex-paper-polisher
description: Use when polishing academic English papers in LaTeX projects through a Terminal-first workflow: macro-level structure analysis, semantic section/paragraph decomposition, conversational revision, direct LaTeX source edits after user confirmation, local git commits, validation, logs, and evolving polishing knowledge.
---

# latex-paper-polisher

## Purpose

Polish academic English LaTeX papers while preserving technical meaning and LaTeX source structure.

## Core Workflow

1. Inspect the current directory as a LaTeX project.
2. Use `scripts/inspect_latex_project.py --map` to build a mechanical project map.
3. Treat the map as source navigation only. Python must not decide polishing units.
4. Main agent reads the main file, section files, references, and relevant project context.
5. Main agent gives a concise macro or section-level analysis before polishing: section role, paragraph purposes, flow issues, terminology risks, and suggested edit order.
6. User chooses a target section, paragraph, or semantic unit in natural language.
7. Main agent splits the target semantically. Short paragraphs are polished as one unit; long paragraphs are split by rhetorical purpose.
8. Main agent and user discuss wording in the terminal until the user confirms the final text.
9. Main agent directly edits the LaTeX source after confirmation.
10. Validate the edit with `scripts/validate_writeback.py` when before/after snippets are available, inspect `git diff`, and run any project-appropriate checks.
11. Append a local-only log entry with `scripts/append_polish_log.py` when a polishing unit is finalized.
12. Commit exactly the confirmed paper-source change in the paper project's own git repository. Do not push unless the user asks.
13. Update this tool repository's `references/knowledge.md` when user preferences or recurring writing rules change.
14. Update this tool repository's `architecture.md` when files, directories, helper responsibilities, or workflow artifacts change.

## Defaults

- Language: academic English only.
- Edit strength: medium polish. Preserve meaning while improving sentence structure, logical flow, and academic expression.
- Unit: model-led semantic unit. Use a whole paragraph when it is short; split longer paragraphs by rhetorical purpose.
- Task decomposition: model-led by the main agent after reading project context.
- Helper scripts: mechanical source mapping, context scaffolding, suggestion validation, logging, and validation only.
- Figures and tables: polish captions or titles only, after reading surrounding context.
- Logs: local only, not pushed to GitHub.
- Knowledge base: global skill references, updated automatically.
- Git: paper projects maintain their own local git history for paper-source edits; this tool repository maintains only tooling, docs, tests, and skill changes.

## Required Checks

- Detect Chinese characters, Chinese punctuation, and full-width symbols in English prose.
- Preserve LaTeX commands and technical meaning.
- Stop before committing if unrelated user changes are present.
- Keep logs, generated context, and temporary artifacts out of Git.
- Commit each confirmed paper-source edit locally in the paper repository with a clear message.
- Do not push paper changes unless the user explicitly asks.
- When files, directories, helper responsibilities, or workflow artifacts change, update `architecture.md`.
- When user preferences, terminology, recurring errors, or process preferences change, update `references/knowledge.md`.

## References

- Section-specific defaults: `references/section-style-rules.md`
- LaTeX preservation rules: `references/latex-preservation.md`
- Log format: `references/log-schema.md`
- Task and specialist-agent protocol: `references/task-protocol.md`
- Evolving knowledge: `references/knowledge.md`
- Project layout and file placement rules: `architecture.md`
