# latex-paper-polisher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first usable `latex-paper-polisher` Codex skill for academic English LaTeX paper polishing.

**Architecture:** The skill uses concise workflow instructions plus deterministic helper scripts. Scripts mechanically index LaTeX projects, generate the current-paragraph HTML workbench, append local logs, and validate writeback safety; Codex remains responsible for reading context, understanding the paper, diagnosing structure, polishing prose, and performing confirmed source edits.

**Tech Stack:** Markdown skill files, Python 3 standard library scripts, pytest tests, static HTML generation, JSON artifacts.

---

## File Structure

- Create `SKILL.md`: skill trigger and core workflow.
- Create `agents/openai.yaml`: UI metadata for the skill.
- Create `references/knowledge.md`: auto-maintained global knowledge base seed.
- Create `references/section-style-rules.md`: default section-specific academic style rules.
- Create `references/latex-preservation.md`: source-preservation rules for writeback.
- Create `references/log-schema.md`: local log schema and storage policy.
- Create `scripts/inspect_latex_project.py`: LaTeX project inspection and paragraph/caption indexing.
- Create `scripts/build_workbench.py`: static current-paragraph HTML workbench writer.
- Create `scripts/append_polish_log.py`: JSONL log appender.
- Create `scripts/validate_writeback.py`: before/after LaTeX construct safety checker.
- Create `tests/fixtures/sample-paper/main.tex`: minimal multi-file LaTeX sample.
- Create `tests/fixtures/sample-paper/sections/introduction.tex`: sample section with paragraphs, citations, math, and figure caption.
- Create `tests/test_inspect_latex_project.py`: project inspection tests.
- Create `tests/test_build_workbench.py`: HTML generation tests.
- Create `tests/test_append_polish_log.py`: log append tests.
- Create `tests/test_validate_writeback.py`: writeback validation tests.

## Task 0: Repository Bootstrap

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Initialize git repository if needed**

Run:

```bash
git rev-parse --show-toplevel || git init
```

Expected: If the project was not already a git repository, `git init` creates one.

- [ ] **Step 2: Create base `.gitignore`**

Create `.gitignore` with:

```gitignore
__pycache__/
.pytest_cache/
.latex-paper-polisher/logs/
*.pyc
```

- [ ] **Step 3: Commit bootstrap files**

Run:

```bash
git add .gitignore docs/superpowers/specs/2026-05-14-latex-paper-polisher-design.md docs/superpowers/plans/2026-05-14-latex-paper-polisher.md
git commit -m "docs: add latex paper polisher design and plan"
```

Expected: The design and plan are committed before implementation begins.

## Task 1: Project Skeleton And Skill Metadata

**Files:**
- Create: `SKILL.md`
- Create: `agents/openai.yaml`
- Create: `references/knowledge.md`
- Create: `references/section-style-rules.md`
- Create: `references/latex-preservation.md`
- Create: `references/log-schema.md`

- [ ] **Step 1: Create skill directory files**

Create the directories:

```bash
mkdir -p agents references scripts tests/fixtures/sample-paper/sections
```

- [ ] **Step 2: Write `SKILL.md`**

Create `SKILL.md` with:

```markdown
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

## References

- Section-specific defaults: `references/section-style-rules.md`
- LaTeX preservation rules: `references/latex-preservation.md`
- Log format: `references/log-schema.md`
- Evolving knowledge: `references/knowledge.md`
```

- [ ] **Step 3: Write `agents/openai.yaml`**

Create `agents/openai.yaml` with:

```yaml
display_name: LaTeX Paper Polisher
short_description: Polish academic English LaTeX papers with structure review, paragraph workbench, logs, and learned preferences.
default_prompt: Review the current LaTeX paper project, diagnose the macro structure, then help polish it paragraph by paragraph while preserving LaTeX source structure.
```

- [ ] **Step 4: Write reference files**

Create `references/knowledge.md` with:

```markdown
# Polishing Knowledge

This file is maintained automatically during paper polishing sessions. The user periodically reviews and corrects it.

## Confirmed Preferences

- Prefer academic English that is clear, precise, and not overstated.

## Section Rules

- See `section-style-rules.md` for defaults. Promote repeated user feedback here when it becomes a stable preference.

## Terminology

Record terms, abbreviations, method names, dataset names, variables, and phrases that must remain consistent.

## Common Errors

- Detect and replace Chinese punctuation, Chinese characters, and full-width symbols in English prose.
- Avoid unnecessary overclaiming.

## Scoped Notes

Use this section for paper-specific or chapter-specific requirements that should not yet become global preferences.
```

Create `references/section-style-rules.md` with:

```markdown
# Section Style Rules

## Abstract

- Be concise.
- State problem, method, key result, and contribution clearly.
- Avoid unsupported claims and unnecessary background detail.

## Introduction

- Build the motivation and gap progressively.
- Make contributions explicit without exaggeration.
- Keep transitions clear between problem, prior limitations, and proposed work.

## Methods

- Prioritize precision, reproducibility, and terminology consistency.
- Preserve equations, variables, and implementation details.

## Results

- Report findings objectively.
- Distinguish observation from interpretation.
- Keep figure and table references accurate.

## Discussion

- Explain implications and limitations.
- Avoid overstating generality.
- Connect results back to the research question.

## Conclusion

- Summarize the main contribution and evidence.
- Avoid introducing new claims.
- Keep future work measured.
```

Create `references/latex-preservation.md` with:

```markdown
# LaTeX Preservation Rules

Do not change these unless the user explicitly requests it or the change is necessary and explained:

- `\cite{...}`, `\parencite{...}`, `\textcite{...}`
- `\ref{...}`, `\autoref{...}`, `\cref{...}`
- `\label{...}`
- inline math `$...$`
- display math and equation-like environments
- figure, table, algorithm, align, equation, and similar environments
- file paths in graphics commands
- custom macros
- comments beginning with `%`

For captions, polish only the natural-language caption text. Preserve labels, figure paths, and references.
```

Create `references/log-schema.md` with:

```markdown
# Log Schema

Local logs are JSON Lines files stored under `.latex-paper-polisher/logs/`.

The log directory must not be pushed to GitHub.

Each entry should contain:

```json
{
  "timestamp": "2026-05-14T00:00:00Z",
  "project_path": "/path/to/paper",
  "source_file": "sections/introduction.tex",
  "section": "Introduction",
  "paragraph_id": "sections/introduction.tex:paragraph:1",
  "original_text": "Original paragraph.",
  "suggested_text": "Suggested paragraph.",
  "user_feedback": "User confirmation or requested change.",
  "final_writeback_text": "Final paragraph.",
  "diff_summary": "One paragraph changed.",
  "validation_result": {"ok": true, "warnings": []},
  "commit_hash": "abc1234",
  "knowledge_updates": []
}
```
```

- [ ] **Step 5: Verify metadata files exist**

Run:

```bash
test -f SKILL.md && test -f agents/openai.yaml && test -f references/knowledge.md
```

Expected: exit code 0.

## Task 2: LaTeX Project Inspector

**Files:**
- Create: `scripts/inspect_latex_project.py`
- Create: `tests/fixtures/sample-paper/main.tex`
- Create: `tests/fixtures/sample-paper/sections/introduction.tex`
- Create: `tests/test_inspect_latex_project.py`

- [ ] **Step 1: Write fixture LaTeX files**

Create `tests/fixtures/sample-paper/main.tex`:

```tex
\documentclass{article}
\usepackage{graphicx}
\begin{document}
\title{Sample Paper}
\maketitle
\begin{abstract}
This paper studies a sample problem， and proposes a method.
\end{abstract}
\input{sections/introduction}
\bibliography{refs}
\end{document}
```

Create `tests/fixtures/sample-paper/sections/introduction.tex`:

```tex
\section{Introduction}
\label{sec:intro}

Prior work has studied this topic~\cite{smith2020}. However, existing methods are often limited when $n$ is large.

We propose a compact method that improves robustness. The main contribution is a clearer analysis of the failure mode.

\begin{figure}
\centering
\includegraphics{figures/example.pdf}
\caption{Overview of the proposed method， including the main processing stages.}
\label{fig:overview}
\end{figure}
```

- [ ] **Step 2: Write failing inspector tests**

Create `tests/test_inspect_latex_project.py`:

```python
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PROJECT = ROOT / "fixtures" / "sample-paper"
SCRIPT = ROOT.parent / "scripts" / "inspect_latex_project.py"


def run_inspector():
    result = subprocess.run(
        ["python", str(SCRIPT), str(PROJECT)],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def test_finds_main_file_and_inputs():
    data = run_inspector()
    assert data["main_file"] == "main.tex"
    assert "sections/introduction.tex" in data["files"]


def test_indexes_sections_paragraphs_and_captions():
    data = run_inspector()
    assert data["sections"][0]["title"] == "Introduction"
    paragraphs = data["paragraphs"]
    assert len(paragraphs) == 3
    assert paragraphs[0]["kind"] == "paragraph"
    assert "Prior work" in paragraphs[0]["text"]
    assert paragraphs[2]["kind"] == "caption"
    assert paragraphs[2]["label"] == "fig:overview"


def test_detects_latex_constructs_and_chinese_punctuation():
    data = run_inspector()
    first = data["paragraphs"][0]
    assert first["citations"] == ["smith2020"]
    assert first["math_spans"] == ["$n$"]
    caption = data["paragraphs"][2]
    assert caption["has_cjk_or_fullwidth"] is True
```

- [ ] **Step 3: Run tests to verify they fail**

Run:

```bash
pytest tests/test_inspect_latex_project.py -q
```

Expected: FAIL because `scripts/inspect_latex_project.py` does not exist.

- [ ] **Step 4: Implement inspector script**

Create `scripts/inspect_latex_project.py`:

```python
#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
SECTION_RE = re.compile(r"\\(section|subsection|subsubsection)\{([^}]+)\}")
CAPTION_RE = re.compile(r"\\caption\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", re.DOTALL)
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
CITE_RE = re.compile(r"\\(?:cite|parencite|textcite|citep|citet)\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:ref|autoref|cref|Cref)\{([^}]+)\}")
MATH_RE = re.compile(r"(?<!\\)\$[^$]+(?<!\\)\$")
CJK_OR_FULLWIDTH_RE = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_tex_suffix(name: str) -> str:
    return name if name.endswith(".tex") else f"{name}.tex"


def find_main_file(project: Path) -> Path:
    tex_files = sorted(project.glob("*.tex"))
    for path in tex_files:
        text = read_text(path)
        if "\\begin{document}" in text:
            return path
    if tex_files:
        return tex_files[0]
    raise SystemExit(f"No .tex files found in {project}")


def expand_files(project: Path, main: Path) -> list[Path]:
    seen: set[Path] = set()
    ordered: list[Path] = []

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in seen:
            return
        seen.add(path)
        ordered.append(path)
        text = read_text(path)
        for match in INPUT_RE.finditer(text):
            child = project / strip_tex_suffix(match.group(1))
            if child.exists():
                visit(child)

    visit(main)
    return ordered


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def extract_constructs(text: str) -> dict:
    citations = []
    for match in CITE_RE.finditer(text):
        citations.extend(part.strip() for part in match.group(1).split(",") if part.strip())
    refs = []
    for match in REF_RE.finditer(text):
        refs.extend(part.strip() for part in match.group(1).split(",") if part.strip())
    return {
        "citations": citations,
        "refs": refs,
        "labels": LABEL_RE.findall(text),
        "math_spans": MATH_RE.findall(text),
        "has_cjk_or_fullwidth": bool(CJK_OR_FULLWIDTH_RE.search(text)),
    }


def paragraph_blocks(text: str) -> list[tuple[int, int, str]]:
    blocks = []
    offset = 0
    for raw in re.split(r"\n\s*\n", text):
        start = text.find(raw, offset)
        offset = start + len(raw)
        block = raw.strip()
        if not block:
            continue
        if block.startswith("\\") and not block.startswith("\\caption"):
            continue
        blocks.append((start, start + len(raw), block))
    return blocks


def inspect_file(project: Path, path: Path) -> tuple[list[dict], list[dict]]:
    rel = path.relative_to(project).as_posix()
    text = read_text(path)
    sections = []
    paragraphs = []
    for match in SECTION_RE.finditer(text):
        sections.append({
            "level": match.group(1),
            "title": match.group(2),
            "file": rel,
            "line": line_number(text, match.start()),
        })

    caption_ranges = []
    for match in CAPTION_RE.finditer(text):
        caption_ranges.append((match.start(), match.end()))
        nearby = text[match.end(): match.end() + 300]
        label_match = LABEL_RE.search(nearby)
        constructs = extract_constructs(match.group(1))
        paragraphs.append({
            "id": f"{rel}:caption:{len(paragraphs) + 1}",
            "kind": "caption",
            "file": rel,
            "start_line": line_number(text, match.start()),
            "end_line": line_number(text, match.end()),
            "text": match.group(1).strip(),
            "label": label_match.group(1) if label_match else None,
            **constructs,
        })

    for start, end, block in paragraph_blocks(text):
        if any(start >= cap_start and end <= cap_end for cap_start, cap_end in caption_ranges):
            continue
        if block.startswith("\\begin") or block.startswith("\\end") or block.startswith("\\section"):
            continue
        constructs = extract_constructs(block)
        paragraphs.append({
            "id": f"{rel}:paragraph:{len(paragraphs) + 1}",
            "kind": "paragraph",
            "file": rel,
            "start_line": line_number(text, start),
            "end_line": line_number(text, end),
            "text": block,
            "label": None,
            **constructs,
        })
    paragraphs.sort(key=lambda item: (item["file"], item["start_line"]))
    return sections, paragraphs


def inspect(project: Path) -> dict:
    project = project.resolve()
    main = find_main_file(project)
    files = expand_files(project, main)
    all_sections = []
    all_paragraphs = []
    for path in files:
        sections, paragraphs = inspect_file(project, path)
        all_sections.extend(sections)
        all_paragraphs.extend(paragraphs)
    return {
        "project": str(project),
        "main_file": main.relative_to(project).as_posix(),
        "files": [path.relative_to(project).as_posix() for path in files],
        "sections": all_sections,
        "paragraphs": all_paragraphs,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: inspect_latex_project.py PROJECT_DIR", file=sys.stderr)
        return 2
    data = inspect(Path(argv[1]))
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 5: Run inspector tests**

Run:

```bash
pytest tests/test_inspect_latex_project.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add scripts/inspect_latex_project.py tests/fixtures/sample-paper/main.tex tests/fixtures/sample-paper/sections/introduction.tex tests/test_inspect_latex_project.py
git commit -m "feat: add LaTeX project inspector"
```

## Task 3: Current Paragraph HTML Workbench

**Files:**
- Create: `scripts/build_workbench.py`
- Create: `tests/test_build_workbench.py`

- [ ] **Step 1: Write failing HTML workbench test**

Create `tests/test_build_workbench.py`:

```python
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
SCRIPT = ROOT.parent / "scripts" / "build_workbench.py"


def test_builds_current_paragraph_html(tmp_path):
    payload = {
        "paragraph_id": "sections/introduction.tex:paragraph:1",
        "source_file": "sections/introduction.tex",
        "section": "Introduction",
        "original_text": "This paper studies a sample problem， and proposes a method.",
        "suggested_text": "This paper studies a sample problem and proposes a method.",
        "rationale": ["Replaced Chinese comma with an English comma.", "Improved academic fluency."],
        "warnings": ["Chinese punctuation detected."],
    }
    payload_path = tmp_path / "payload.json"
    output_path = tmp_path / "workbench.html"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")

    subprocess.run(
        ["python", str(SCRIPT), str(payload_path), str(output_path)],
        check=True,
    )

    html = output_path.read_text(encoding="utf-8")
    assert "Current Paragraph" in html
    assert "Original" in html
    assert "Suggested Revision" in html
    assert "Chinese punctuation detected." in html
    assert "sections/introduction.tex:paragraph:1" in html
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_build_workbench.py -q
```

Expected: FAIL because `scripts/build_workbench.py` does not exist.

- [ ] **Step 3: Implement HTML workbench script**

Create `scripts/build_workbench.py`:

```python
#!/usr/bin/env python3
import html
import json
import sys
from pathlib import Path


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def list_items(items: list[str]) -> str:
    if not items:
        return "<li>None.</li>"
    return "\n".join(f"<li>{esc(item)}</li>" for item in items)


def render(payload: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>LaTeX Paper Polisher</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 32px; line-height: 1.55; color: #1f2933; }}
    main {{ max-width: 1100px; margin: 0 auto; }}
    h1 {{ font-size: 28px; margin-bottom: 4px; }}
    .meta {{ color: #52606d; margin-bottom: 24px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
    section {{ border: 1px solid #d9e2ec; border-radius: 8px; padding: 16px; background: #fff; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; font-family: ui-monospace, monospace; }}
    .full {{ grid-column: 1 / -1; }}
    .warning {{ color: #9f580a; }}
  </style>
</head>
<body>
<main>
  <h1>Current Paragraph</h1>
  <div class="meta">{esc(payload.get("paragraph_id", ""))} · {esc(payload.get("source_file", ""))} · {esc(payload.get("section", ""))}</div>
  <div class="grid">
    <section>
      <h2>Original</h2>
      <pre>{esc(payload.get("original_text", ""))}</pre>
    </section>
    <section>
      <h2>Suggested Revision</h2>
      <pre>{esc(payload.get("suggested_text", ""))}</pre>
    </section>
    <section>
      <h2>Rationale</h2>
      <ul>{list_items(payload.get("rationale", []))}</ul>
    </section>
    <section>
      <h2>Warnings</h2>
      <ul class="warning">{list_items(payload.get("warnings", []))}</ul>
    </section>
    <section class="full">
      <h2>Confirmation</h2>
      <p>Review this paragraph in the browser, then confirm or revise it in the Codex conversation. This page does not write to source files.</p>
    </section>
  </div>
</main>
</body>
</html>
"""


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: build_workbench.py PAYLOAD_JSON OUTPUT_HTML", file=sys.stderr)
        return 2
    payload = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    Path(argv[2]).write_text(render(payload), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 4: Run workbench tests**

Run:

```bash
pytest tests/test_build_workbench.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add scripts/build_workbench.py tests/test_build_workbench.py
git commit -m "feat: add paragraph HTML workbench"
```

## Task 4: Local Log Appender

**Files:**
- Create: `scripts/append_polish_log.py`
- Create: `tests/test_append_polish_log.py`
- Modify: `.gitignore`

- [ ] **Step 1: Write failing log test**

Create `tests/test_append_polish_log.py`:

```python
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
SCRIPT = ROOT.parent / "scripts" / "append_polish_log.py"


def test_appends_jsonl_entry(tmp_path):
    entry = {
        "timestamp": "2026-05-14T00:00:00Z",
        "project_path": "/paper",
        "source_file": "main.tex",
        "section": "Abstract",
        "paragraph_id": "main.tex:paragraph:1",
        "original_text": "Original.",
        "suggested_text": "Suggested.",
        "user_feedback": "Accepted.",
        "final_writeback_text": "Suggested.",
        "diff_summary": "One paragraph changed.",
        "validation_result": {"ok": True, "warnings": []},
        "commit_hash": "abc1234",
        "knowledge_updates": [],
    }
    entry_path = tmp_path / "entry.json"
    log_path = tmp_path / "polish.jsonl"
    entry_path.write_text(json.dumps(entry), encoding="utf-8")

    subprocess.run(["python", str(SCRIPT), str(entry_path), str(log_path)], check=True)
    subprocess.run(["python", str(SCRIPT), str(entry_path), str(log_path)], check=True)

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["paragraph_id"] == "main.tex:paragraph:1"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_append_polish_log.py -q
```

Expected: FAIL because `scripts/append_polish_log.py` does not exist.

- [ ] **Step 3: Implement log appender**

Create `scripts/append_polish_log.py`:

```python
#!/usr/bin/env python3
import json
import sys
from pathlib import Path


REQUIRED_KEYS = {
    "timestamp",
    "project_path",
    "source_file",
    "section",
    "paragraph_id",
    "original_text",
    "suggested_text",
    "user_feedback",
    "final_writeback_text",
    "diff_summary",
    "validation_result",
    "commit_hash",
    "knowledge_updates",
}


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: append_polish_log.py ENTRY_JSON LOG_JSONL", file=sys.stderr)
        return 2
    entry_path = Path(argv[1])
    log_path = Path(argv[2])
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    missing = sorted(REQUIRED_KEYS - set(entry))
    if missing:
        print(f"missing required log keys: {', '.join(missing)}", file=sys.stderr)
        return 1
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 4: Add local log ignore rule**

Create or update `.gitignore` with:

```gitignore
.latex-paper-polisher/logs/
```

- [ ] **Step 5: Run log tests**

Run:

```bash
pytest tests/test_append_polish_log.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add .gitignore scripts/append_polish_log.py tests/test_append_polish_log.py
git commit -m "feat: add local polish log appender"
```

## Task 5: Writeback Validator

**Files:**
- Create: `scripts/validate_writeback.py`
- Create: `tests/test_validate_writeback.py`

- [ ] **Step 1: Write failing validator tests**

Create `tests/test_validate_writeback.py`:

```python
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
SCRIPT = ROOT.parent / "scripts" / "validate_writeback.py"


def run_validator(before: str, after: str, tmp_path: Path):
    before_path = tmp_path / "before.tex"
    after_path = tmp_path / "after.tex"
    before_path.write_text(before, encoding="utf-8")
    after_path.write_text(after, encoding="utf-8")
    result = subprocess.run(
        ["python", str(SCRIPT), str(before_path), str(after_path)],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def test_validator_passes_when_construct_counts_match(tmp_path):
    before = "Text~\\cite{a}. See Fig.~\\ref{fig:x}. $n=1$"
    after = "Clearer text~\\cite{a}. See Fig.~\\ref{fig:x}. $n=1$"
    data = run_validator(before, after, tmp_path)
    assert data["ok"] is True
    assert data["warnings"] == []


def test_validator_warns_when_citation_removed(tmp_path):
    before = "Text~\\cite{a}. See Fig.~\\ref{fig:x}."
    after = "Clearer text. See Fig.~\\ref{fig:x}."
    data = run_validator(before, after, tmp_path)
    assert data["ok"] is False
    assert any("cite" in warning for warning in data["warnings"])
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_validate_writeback.py -q
```

Expected: FAIL because `scripts/validate_writeback.py` does not exist.

- [ ] **Step 3: Implement validator**

Create `scripts/validate_writeback.py`:

```python
#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


PATTERNS = {
    "cite": re.compile(r"\\(?:cite|parencite|textcite|citep|citet)\{[^}]+\}"),
    "ref": re.compile(r"\\(?:ref|autoref|cref|Cref)\{[^}]+\}"),
    "label": re.compile(r"\\label\{[^}]+\}"),
    "inline_math": re.compile(r"(?<!\\)\$[^$]+(?<!\\)\$"),
    "begin_env": re.compile(r"\\begin\{[^}]+\}"),
    "end_env": re.compile(r"\\end\{[^}]+\}"),
}


def counts(text: str) -> dict[str, int]:
    return {name: len(pattern.findall(text)) for name, pattern in PATTERNS.items()}


def validate(before: str, after: str) -> dict:
    before_counts = counts(before)
    after_counts = counts(after)
    warnings = []
    for name, before_count in before_counts.items():
        after_count = after_counts[name]
        if before_count != after_count:
            warnings.append(f"{name} count changed from {before_count} to {after_count}")
    return {
        "ok": not warnings,
        "warnings": warnings,
        "before_counts": before_counts,
        "after_counts": after_counts,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: validate_writeback.py BEFORE_TEX AFTER_TEX", file=sys.stderr)
        return 2
    before = Path(argv[1]).read_text(encoding="utf-8")
    after = Path(argv[2]).read_text(encoding="utf-8")
    print(json.dumps(validate(before, after), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 4: Run validator tests**

Run:

```bash
pytest tests/test_validate_writeback.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add scripts/validate_writeback.py tests/test_validate_writeback.py
git commit -m "feat: add LaTeX writeback validator"
```

## Task 6: End-To-End Smoke Test

**Files:**
- Create: `tests/test_smoke_workflow.py`

- [ ] **Step 1: Write smoke test**

Create `tests/test_smoke_workflow.py`:

```python
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PROJECT = ROOT / "fixtures" / "sample-paper"
INSPECT = ROOT.parent / "scripts" / "inspect_latex_project.py"
WORKBENCH = ROOT.parent / "scripts" / "build_workbench.py"
LOGGER = ROOT.parent / "scripts" / "append_polish_log.py"
VALIDATOR = ROOT.parent / "scripts" / "validate_writeback.py"


def test_index_to_workbench_to_log_to_validation(tmp_path):
    inspected = subprocess.run(
        ["python", str(INSPECT), str(PROJECT)],
        check=True,
        text=True,
        capture_output=True,
    )
    data = json.loads(inspected.stdout)
    paragraph = data["paragraphs"][0]
    payload = {
        "paragraph_id": paragraph["id"],
        "source_file": paragraph["file"],
        "section": "Introduction",
        "original_text": paragraph["text"],
        "suggested_text": paragraph["text"].replace("However", "However,"),
        "rationale": ["Improved transition punctuation."],
        "warnings": [],
    }
    payload_path = tmp_path / "payload.json"
    html_path = tmp_path / "workbench.html"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    subprocess.run(["python", str(WORKBENCH), str(payload_path), str(html_path)], check=True)
    assert html_path.exists()

    before_path = tmp_path / "before.tex"
    after_path = tmp_path / "after.tex"
    before_path.write_text(paragraph["text"], encoding="utf-8")
    after_path.write_text(payload["suggested_text"], encoding="utf-8")
    validation = subprocess.run(
        ["python", str(VALIDATOR), str(before_path), str(after_path)],
        check=True,
        text=True,
        capture_output=True,
    )
    validation_data = json.loads(validation.stdout)
    assert validation_data["ok"] is True

    log_entry = {
        "timestamp": "2026-05-14T00:00:00Z",
        "project_path": str(PROJECT),
        "source_file": paragraph["file"],
        "section": "Introduction",
        "paragraph_id": paragraph["id"],
        "original_text": paragraph["text"],
        "suggested_text": payload["suggested_text"],
        "user_feedback": "Accepted.",
        "final_writeback_text": payload["suggested_text"],
        "diff_summary": "One paragraph changed.",
        "validation_result": validation_data,
        "commit_hash": "not-committed-in-test",
        "knowledge_updates": [],
    }
    entry_path = tmp_path / "entry.json"
    log_path = tmp_path / "polish.jsonl"
    entry_path.write_text(json.dumps(log_entry), encoding="utf-8")
    subprocess.run(["python", str(LOGGER), str(entry_path), str(log_path)], check=True)
    assert len(log_path.read_text(encoding="utf-8").splitlines()) == 1
```

- [ ] **Step 2: Run smoke test**

Run:

```bash
pytest tests/test_smoke_workflow.py -q
```

Expected: PASS.

- [ ] **Step 3: Run all tests**

Run:

```bash
pytest -q
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

Run:

```bash
git add tests/test_smoke_workflow.py
git commit -m "test: add polishing workflow smoke test"
```

## Task 7: Final Review And Documentation Check

**Files:**
- Modify: `docs/superpowers/specs/2026-05-14-latex-paper-polisher-design.md` only if implementation decisions require clarifying the spec.
- Modify: `docs/superpowers/plans/2026-05-14-latex-paper-polisher.md` only if execution discovers a plan error.

- [ ] **Step 1: Verify no local-only logs are tracked**

Run:

```bash
git status --short
```

Expected: no `.latex-paper-polisher/logs/` files appear.

- [ ] **Step 2: Verify skill metadata and tests**

Run:

```bash
python scripts/inspect_latex_project.py tests/fixtures/sample-paper > /tmp/latex-paper-polisher-index.json
pytest -q
```

Expected: JSON file is written and all tests pass.

- [ ] **Step 3: Inspect generated index manually**

Run:

```bash
python -m json.tool /tmp/latex-paper-polisher-index.json | sed -n '1,120p'
```

Expected: output shows `main.tex`, `sections/introduction.tex`, `Introduction`, two natural paragraphs, and one caption.

- [ ] **Step 4: Final commit for any documentation adjustments**

If docs changed:

```bash
git add docs/superpowers/specs/2026-05-14-latex-paper-polisher-design.md docs/superpowers/plans/2026-05-14-latex-paper-polisher.md
git commit -m "docs: align latex paper polisher plan"
```

If docs did not change, skip this commit.
