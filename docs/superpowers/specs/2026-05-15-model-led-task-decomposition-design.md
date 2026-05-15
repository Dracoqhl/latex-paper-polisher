# Model-Led Task Decomposition Design

## Purpose

Phase 2 shifts `latex-paper-polisher` from Python-led paragraph parsing to model-led task decomposition. Python remains useful for mechanical project mapping, but it must not decide which text units should be polished. The main agent reads the paper structure, plans the polishing workflow, tracks progress, and controls writeback. Specialist agents may review or polish scoped sections, but they only return structured suggestions.

This direction is based on the observed ICML 2026 paper project at `/data/proj/icml2026/ICML2026`, which has a clear `example_paper.tex` entrypoint and section files under `src/`. The current inspector can discover that structure, but it also misclassifies preamble, comments, tables, raw boxes, and appendix blocks as natural paragraphs. That confirms that Python should provide a source map rather than a semantic paragraph splitter.

## Workflow

1. Build a read-only project map.
2. Main agent reads the map, main file, and section files.
3. Main agent produces a paper-level task plan organized by section, caption, consistency pass, and macro-review pass.
4. User confirms the task order and optimization direction.
5. Specialist agents produce scoped review or polishing suggestions for one task at a time.
6. Main agent reviews the suggestions for consistency with paper context, LaTeX preservation rules, and user preferences.
7. User confirms the final text.
8. Main agent performs the only source writeback, validates the diff, appends a local log entry, commits, and pushes.

## Roles

### Project Mapper

The mapper is a deterministic helper script. It should discover:

- main `.tex` file
- expanded `\input` and `\include` file tree
- section and subsection anchors
- labels, references, citations, captions, and math-like spans
- line ranges and nearby source context

It should not classify prose quality, infer paper intent, or decide polishing units. It may mark obviously protected regions such as preamble, bibliography commands, raw LaTeX environments, and generated artifacts, but those marks are advisory.

### Main Agent

The main agent owns coordination:

- reads the paper and project map
- identifies section roles and paper argument flow
- decomposes work into explicit tasks
- tracks task status
- maintains terminology and user preferences
- decides what context a specialist agent receives
- reviews specialist outputs before showing them to the user
- performs writeback only after user confirmation

The main agent must keep a single source of truth for progress so that work can resume across sessions.

### Specialist Agents

Specialist agents are optional and scoped. They may handle:

- macro reviewer diagnosis
- section-level polishing suggestions
- caption polishing suggestions
- terminology consistency checks
- Chinese/full-width punctuation scan

They must not edit files or commit changes. Their output must be structured: target source, proposed revision, rationale, preserved LaTeX constructs, risks, and open questions.

## Data Artifacts

### Project Map

`project_map.json` is generated from the current LaTeX project and may be written outside the paper directory for read-only testing. It contains mechanical source information only:

- `project_root`
- `main_file`
- `files`
- `sections`
- `captions`
- `labels`
- `refs`
- `citations`
- `protected_regions`

### Task Plan

The main agent creates a task plan from the source map and paper reading. A task has:

- `id`
- `type`
- `title`
- `target_files`
- `anchors`
- `status`
- `assigned_role`
- `required_context`
- `acceptance_check`

Initial task types should include:

- `macro_review`
- `section_polish`
- `caption_polish`
- `terminology_check`
- `latex_safety_check`
- `cjk_fullwidth_scan`

### Specialist Output

Specialist output should include:

- `task_id`
- `target`
- `original_text`
- `proposed_text`
- `rationale`
- `latex_constructs_preserved`
- `risks`
- `questions`

## Read-Only Real Paper Validation

The ICML project at `/data/proj/icml2026/ICML2026` may be used for validation, but Phase 2 tests must not modify it. Any generated project map, task plan draft, or workbench payload for that paper must be written under `/tmp` or the `latex-paper-polisher` repository test output area.

Validation should confirm that the system can:

- detect `example_paper.tex` as the main file
- discover section files under `src/`
- list the main paper sections in source order
- avoid presenting preamble and package configuration as normal polishing tasks
- generate a section-oriented task plan for Abstract, Introduction, Related Work, main analysis sections, Conclusion, Limitations, and Appendix

## Implementation Direction

Phase 2 should revise the existing skill and helper scripts rather than add a full LaTeX parser.

- Rename or reframe the inspector as a project mapper in docs and skill instructions.
- Add a task-plan schema/reference document.
- Add a task-plan builder helper only if it remains mechanical; semantic task decomposition remains the main agent's responsibility.
- Update tests to assert source-map quality and read-only behavior, not perfect paragraph segmentation.
- Preserve existing helper scripts where useful, but stop treating blank-line paragraphs as the primary workflow boundary.

## Acceptance Criteria

- The skill instructions clearly state that Python does not decide polishing units.
- The project mapper produces a useful source map for the sample fixture.
- Read-only validation against `/data/proj/icml2026/ICML2026` writes no files inside that paper directory.
- The main-agent workflow includes task decomposition before paragraph polishing.
- Specialist agents are constrained to suggestions only.
- Writeback remains centralized in the main agent after user confirmation.

## Assumptions

- Most target papers have clear file trees or section files.
- The main agent has enough context to read section files and choose meaningful polishing tasks.
- Parallel specialist work should be introduced conservatively after the task protocol is stable.
- The existing writeback validator and local log appender remain useful in later phases.
