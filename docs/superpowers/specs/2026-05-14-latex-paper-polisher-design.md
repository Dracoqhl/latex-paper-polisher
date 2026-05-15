# latex-paper-polisher Design

## Purpose

`latex-paper-polisher` is a Codex skill for polishing academic English papers written as LaTeX projects. It supports two modes of work:

1. A macro-level, reviewer-style analysis of the paper structure and argument flow.
2. Paragraph-by-paragraph polishing through a continuously updated HTML workbench.

The skill is intended to improve over time. It maintains a global knowledge base for writing preferences, section-specific style rules, terminology, and common error patterns.

## Scope

The skill targets academic English only.

It should detect and correct Chinese characters, Chinese punctuation, and full-width symbols when they appear in English paper text.

It should parse the current directory as a LaTeX project, but parsing must not replace Codex's paper understanding. Scripts provide mechanical indexes and source locations. Codex must still read the paper context, understand the argument, and make polishing decisions.

## Recommended Architecture

The selected approach is a skill with lightweight helper scripts and a continuously updated HTML workbench.

### 1. LaTeX Project Indexing

Helper scripts find the main `.tex` file, expand `\input` and `\include`, and build indexes for:

- chapters and sections
- natural paragraphs
- figure and table captions
- labels, refs, citations, and math environments
- source file paths and line ranges
- nearby context windows

This layer produces a map of the project. It does not make semantic judgments.

### 2. Codex Understanding And Diagnosis

Codex uses the index to read the real paper context. Before paragraph polishing, it performs a detailed reviewer-style diagnosis:

- section roles
- argument chain
- contribution framing
- evidence and experiment support
- section transitions
- likely reviewer concerns
- reader comprehension burden

Codex confirms the overall optimization direction with the user before moving into paragraph-level polishing.

### 3. HTML Paragraph Workbench

The HTML workbench is a persistent page that shows only the current paragraph or caption. It does not accumulate history. After a paragraph is completed, the full record goes into the local log and the page switches to the next paragraph.

The default view includes:

- original text
- one medium-strength suggested revision
- concise rationale
- Chinese character and punctuation checks
- terminology and LaTeX preservation warnings
- source location

The default polishing strength is medium: preserve the original meaning, but allow sentence restructuring, clearer logical connections, and more natural academic English.

### 4. Natural-Language Confirmation And Writeback

The first version does not need an HTML "complete" button.

The user confirms work in natural language, for example:

- "This paragraph is fine."
- "Use my edited version."
- "Keep the second sentence closer to the original."
- "Make this part emphasize the experimental result."

After confirmation, Codex writes the final version back into the LaTeX source file.

### 5. Log, Git, And Knowledge Maintenance

Each paragraph writeback directly modifies the LaTeX source file and writes a local log entry. Each paragraph-level source change becomes one Git commit and is pushed to GitHub.

Logs are local only and must not be pushed.

The global skill knowledge base is updated automatically. The user will periodically review it and correct inappropriate rules.

At stage boundaries, such as after a chapter or after one full polishing pass, the skill should ask whether to create and push a Git tag.

## Proposed Directory Structure

```text
latex-paper-polisher/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── inspect_latex_project.py
│   ├── build_workbench.py
│   ├── append_polish_log.py
│   └── validate_writeback.py
└── references/
    ├── knowledge.md
    ├── section-style-rules.md
    ├── latex-preservation.md
    └── log-schema.md
```

## File Responsibilities

### SKILL.md

The skill file should stay concise. It should describe:

- trigger conditions
- required order: macro diagnosis before paragraph polishing
- English-only academic polishing
- Chinese character and punctuation detection
- medium-strength default polishing
- natural paragraph default segmentation
- figure and table caption handling
- natural-language confirmation before writeback
- paragraph-level commit and push behavior
- local-only logs
- automatic knowledge-base maintenance

### scripts/inspect_latex_project.py

Responsibilities:

- locate the main `.tex` file
- expand `\input` and `\include`
- build the section tree
- identify natural paragraphs based on blank-line boundaries
- identify figure and table captions
- preserve source file and line location metadata
- identify labels, refs, citations, and math environments
- output structured JSON for Codex and other helper scripts

This script must not judge writing quality or infer paper intent.

### scripts/build_workbench.py

Responsibilities:

- generate or refresh the current HTML workbench
- show one paragraph or caption at a time
- display original text, revision, rationale, checks, and location
- avoid accumulating completed paragraph history in the page

### scripts/append_polish_log.py

Responsibilities:

- append one log entry per completed paragraph or caption
- include source location, original text, suggestion, user feedback, final text, diff summary, commit hash, and knowledge updates
- store logs in a local-only ignored directory

### scripts/validate_writeback.py

Responsibilities:

- check the intended paragraph was changed
- check unrelated paragraphs were not changed
- compare counts of sensitive LaTeX constructs before and after
- flag possible damage to citations, labels, refs, math, environments, and comments
- optionally run a fast compile command if the project supports it

Validation helps catch mechanical damage. It does not replace Codex's semantic review.

### references/knowledge.md

The global auto-maintained knowledge base.

It should include:

- confirmed writing preferences
- terminology
- common error patterns
- section-specific preferences
- scoped notes for temporary or paper-specific requirements

### references/section-style-rules.md

Default academic conventions by paper section.

Initial sections should include:

- Abstract
- Introduction
- Methods
- Results
- Discussion
- Conclusion

Rules should start from academic convention and evolve toward the user's preferences.

### references/latex-preservation.md

Rules for preserving LaTeX source structure during writeback.

### references/log-schema.md

The stable log schema so logs are consistent across sessions.

## Detailed Workflow

1. Enter the current LaTeX project directory.
2. Check that it is a LaTeX project.
3. Check git state, GitHub remote, and unrelated uncommitted changes.
4. Ensure the local log directory is ignored by git.
5. Run project indexing.
6. Read the relevant LaTeX source and context.
7. Produce macro-level reviewer-style diagnosis.
8. Confirm the macro optimization direction with the user.
9. Begin paragraph-level polishing.
10. Refresh the HTML workbench for the current paragraph.
11. Wait for user feedback or confirmation in natural language.
12. Write the final version back into the source `.tex`.
13. Validate the writeback.
14. Append a local log entry.
15. Commit the paragraph-level source change.
16. Push to GitHub.
17. Update the global skill knowledge base automatically.
18. Move to the next paragraph.
19. At stage boundaries, ask whether to create and push a Git tag.

## Paragraph And Caption Handling

The default unit is a natural paragraph split by blank lines.

Figure and table content is not polished. Only captions and titles are polished. Before changing a caption, Codex must read surrounding text, the figure/table environment, labels, citations, and nearby references so that the caption is not semantically changed in the wrong direction.

## LaTeX Preservation Rules

Writeback should only replace natural-language text by default. It should not proactively change:

- `\cite{...}`, `\ref{...}`, `\label{...}`, `\autoref{...}`
- inline math and display math
- equation, align, figure, table, algorithm, and similar environments
- `\input`, `\include`, bibliography commands
- comments
- custom macros
- file paths
- labels and citation keys

If a change near these constructs is necessary, Codex should explain the risk before modifying it.

## English Quality Rules

Default checks:

- academic tone
- grammar and fluency
- logical transitions
- topic sentence clarity
- terminology consistency
- Chinese characters, Chinese punctuation, and full-width symbols
- overclaiming
- preservation of technical meaning

## Git And Log Rules

Each paragraph or caption writeback is one commit.

After each commit, push to GitHub.

The commit must not include local logs.

If unrelated uncommitted changes exist, stop and report them before committing.

If push fails, keep the local commit and report the failure.

At stage boundaries, ask whether to create and push a Git tag. Tags are not automatic.

## Local Log Schema

Each completed paragraph should record:

```text
timestamp
project_path
source_file
section
paragraph_id
original_text
suggested_text
user_feedback
final_writeback_text
diff_summary
validation_result
commit_hash
knowledge_updates
```

Logs should live in a local-only ignored directory such as:

```text
.latex-paper-polisher/logs/
```

## Knowledge Base Rules

The knowledge base is maintained automatically in the global skill directory.

It should distinguish:

- `confirmed_preferences`: repeated or explicit user writing preferences
- `section_rules`: rules for abstract, results, discussion, conclusion, and other sections
- `terminology`: terms, abbreviations, method names, variables, and phrases that must remain consistent
- `common_errors`: recurring issues such as Chinese punctuation, verbose sentences, weak transitions, and overuse of words such as "significant"
- `scoped_notes`: temporary or paper-specific requirements

To reduce incorrect learning:

- Single-use requirements should begin as scoped notes.
- Repeated patterns may be promoted to confirmed preferences.
- Terminology entries should keep source context.
- If the user corrects the knowledge base, update or remove the outdated rule.

## Open Questions For Implementation

- Exact JSON schema for the LaTeX project index.
- Whether to implement a minimal static HTML workbench first or a small local file watcher.
- How much compile validation should be attempted by default when a project has no known build command.
- Whether the skill repository itself should be initialized and pushed as a standalone GitHub repository.
