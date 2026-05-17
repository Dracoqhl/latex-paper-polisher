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
3. Follow `references/terminal-polishing-workflow.md` for the direct-edit safety loop.
4. Treat the map as source navigation only. Python must not decide polishing units.
5. Main agent reads the main file, section files, references, and relevant project context.
6. Main agent gives a concise macro or section-level analysis before polishing: section role, paragraph purposes, flow issues, terminology risks, and suggested edit order.
7. User chooses a target section, paragraph, or semantic unit in natural language.
8. Main agent splits the target semantically. Short paragraphs are polished as one unit; long paragraphs are split by rhetorical purpose.
9. Main agent presents a review package before editing: file location, current source text, proposed revision, rationale, and risks/questions. Do not edit source from an unreviewed proposal.
10. Main agent and user discuss wording in the terminal until the user explicitly accepts, rejects, or revises each proposed change.
11. Main agent directly edits the LaTeX source only for accepted changes.
12. Validate the edit with `scripts/validate_writeback.py` when before/after snippets are available, inspect `git diff`, and run any project-appropriate checks.
13. Append a local-only log entry with `scripts/record_terminal_polish_session.py` when a polishing unit is finalized and committed.
14. Commit exactly the confirmed paper-source change in the paper project's own git repository. Push only when the user has requested pushing for that project or change.
15. Update this tool repository's `references/knowledge.md` when user preferences or recurring writing rules change.
16. Update this tool repository's `architecture.md` when files, directories, helper responsibilities, or workflow artifacts change.

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
- For polishing or rebuttal-driven edits, always show a review package and wait for user confirmation before editing source.
- Push paper changes only when the user has explicitly requested pushing for that project or change.
- When files, directories, helper responsibilities, or workflow artifacts change, update `architecture.md`.
- When user preferences, terminology, recurring errors, or process preferences change, update `references/knowledge.md`.

## References

- Section-specific defaults: `references/section-style-rules.md`
- Terminal-first workflow: `references/terminal-polishing-workflow.md`
- LaTeX preservation rules: `references/latex-preservation.md`
- Log format: `references/log-schema.md`
- Task and specialist-agent protocol: `references/task-protocol.md`
- Evolving knowledge: `references/knowledge.md`
- Project layout and file placement rules: `architecture.md`
