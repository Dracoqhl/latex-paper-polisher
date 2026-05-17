# Polishing Knowledge

This file is maintained automatically during paper polishing sessions. The user periodically reviews and corrects it.

## Confirmed Preferences

- Prefer academic English that is clear, precise, and not overstated.
- Maintain `architecture.md` alongside functional or file-structure changes. It is the source of truth for intended project layout and file placement rules.
- When future work updates files or functionality, update both the evolving knowledge base and `architecture.md` when their contents are affected.
- Python helpers should not own semantic paragraph splitting. They should provide source maps and validation only; the main agent should decompose polishing tasks after reading the paper.
- Specialist agents are suggestion-only by default. The main agent keeps exclusive writeback authority and reviews all suggestions before presenting final text to the user.
- Use `/data/latex_test` for manual external validation outputs when testing real LaTeX projects.
- Before polishing a real paper, Codex should inspect the paper tree and read enough source context to form a paper-level or section-level understanding before suggesting text changes.
- The active workflow is Terminal-first. The user names a section or semantic target, Codex analyzes section role, paragraph purposes, flow issues, terminology risks, and likely edit order in the terminal.
- Do not maintain a separate HTML polishing workbench as the default workflow. The terminal conversation is the primary interface.
- Short paragraphs can be polished as one unit. Long paragraphs should be split by semantic or rhetorical purpose before revision.
- For section polishing, use one fresh specialist-agent context per section when specialist help is useful; specialist agents remain suggestion-only and must not edit files.
- Validate specialist suggestion JSON before using it in terminal discussion. Specialist suggestions remain advisory and must not directly edit source.
- After the user confirms final wording, Codex should directly edit the paper source file, validate, review `git diff`, and commit in the paper project's own git repository.
- For polishing or rebuttal-driven edits, Codex should first present a review package with the current source text, proposed revision, rationale, and risks/questions. Source files should be edited only after the user accepts the proposed change.
- Push paper-project commits when the user has explicitly requested pushing for that project or change.
- The tool repository has its own git history for scripts, docs, tests, and skill changes. Paper repositories have separate git histories for paper-source edits.

## Section Rules

- See `section-style-rules.md` for defaults. Promote repeated user feedback here when it becomes a stable preference.

## Terminology

Record terms, abbreviations, method names, dataset names, variables, and phrases that must remain consistent.

## Common Errors

- Detect and replace Chinese punctuation, Chinese characters, and full-width symbols in English prose.
- Avoid unnecessary overclaiming.

## Scoped Notes

Use this section for paper-specific or chapter-specific requirements that should not yet become global preferences.
