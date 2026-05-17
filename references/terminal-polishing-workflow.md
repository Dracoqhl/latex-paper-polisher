# Terminal Polishing Workflow

This is the active workflow for polishing LaTeX papers. It replaces the removed browser workbench flow.

## 1. Confirm Paper Git State

Run the paper git guard before editing source:

```bash
python /data/latex-paper-polisher/scripts/check_paper_git.py /path/to/paper
```

Continue only when the target is a git repository and the dirty files are understood. If the directory is not a git repository, ask before initializing git. If unrelated dirty files are present, stop and ask how to proceed.

## 2. Read Context

Use the mechanical project map for navigation, not for semantic decisions:

```bash
python /data/latex-paper-polisher/scripts/inspect_latex_project.py --map /path/to/paper /tmp/project-map.json
```

Then read the relevant `.tex` files directly. For a section-level request, read the target section plus enough neighboring text to understand flow, terminology, and paper-level claims.

## 3. Analyze Before Editing

Before proposing wording, give a concise analysis:

- section role in the paper
- paragraph or semantic-unit purpose
- flow and transition issues
- overclaiming or terminology risks
- suggested edit order

Do not let Python decide semantic split boundaries. The main agent decides whether to polish a whole paragraph or split a long paragraph by rhetorical purpose.

## 4. Present A Review Package

Before editing source, present a compact review package for each proposed change:

- file path and section
- current source text
- proposed revised text
- rationale for the change
- risks or questions that need user confirmation

This package is the decision surface. Do not edit `.tex` files from an unreviewed proposal, even when the change appears mechanical. For broad tasks, split the work into small packages that the user can accept, reject, or revise independently.

For mechanical consistency edits, combine related occurrences into one batch review package instead of presenting each occurrence separately. Examples include terminology normalization, Chinese punctuation cleanup, and full-width symbol cleanup. The batch package must list every affected location with concise local context and a before/after replacement. Apply the batch only after the user confirms it.

## 5. Discuss One Semantic Unit

Work on one unit at a time. Present the original text, the proposed revision, and the reason for the change. The user may ask for alternative styles, stronger or weaker claims, or narrower terminology.

Do not edit source until the user confirms the final wording.

## 6. Apply Confirmed Source Edit

After confirmation, edit the LaTeX source directly and only for the accepted items. Preserve commands, citations, labels, refs, math, comments, and intentional formatting.

Keep edits scoped to the confirmed unit. If a broader nearby edit becomes necessary, explain it before editing.

## 7. Validate And Inspect

When before/after snippets are available, run:

```bash
python /data/latex-paper-polisher/scripts/validate_writeback.py /tmp/before.tex /tmp/after.tex
```

Inspect the paper repository diff:

```bash
git -C /path/to/paper diff -- path/to/source.tex
```

Run project-specific build or lint checks when available and proportional to the edit.

## 8. Commit In Paper Repository

Commit each confirmed paper-source change in the paper project's own git repository:

```bash
git -C /path/to/paper add path/to/source.tex
git -C /path/to/paper commit -m "polish: refine abstract motivation"
```

Push only when the user has requested pushing for that project or change.

## 9. Record Session And Knowledge

If the edit is substantive, append a terminal polishing session log after the paper commit:

```bash
python /data/latex-paper-polisher/scripts/record_terminal_polish_session.py session.json /path/to/paper/.latex-paper-polisher/logs/terminal-polish.jsonl
```

Update `references/knowledge.md` in this tool repository when the user expresses a reusable writing preference, terminology rule, or process preference. Commit tool-repository documentation changes separately from paper-source commits.
