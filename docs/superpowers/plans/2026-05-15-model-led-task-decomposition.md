# Model-Led Task Decomposition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Phase 2 of `latex-paper-polisher`: move from Python-led paragraph splitting to model-led paper task decomposition with deterministic source mapping and structured specialist-agent suggestion protocols.

**Architecture:** Python scripts provide read-only mechanical maps and optional task skeletons; they do not decide semantic polishing units. The main agent owns paper understanding, task decomposition, progress tracking, and source writeback. Specialist agents only return structured suggestions and never edit files.

**Tech Stack:** Python 3 standard library, pytest, Markdown reference docs, JSON artifacts, existing Codex skill layout.

---

## File Structure

- Modify `SKILL.md`: rewrite the workflow around project mapping, main-agent task decomposition, specialist suggestion-only roles, and centralized writeback.
- Modify `architecture.md`: document the Phase 2 placement rules for mapper outputs, task protocol docs, and generated task skeletons.
- Modify `references/knowledge.md`: record the confirmed process preference that Python should not own semantic paragraph splitting.
- Create `references/task-protocol.md`: stable schema for task plans and specialist-agent outputs.
- Modify `scripts/inspect_latex_project.py`: extend it into a project mapper that outputs source-map fields while keeping the existing paragraph/caption behavior available for current tests.
- Create `scripts/build_task_skeleton.py`: build a mechanical starter task skeleton from project-map JSON; the main agent may edit or replace it after reading the paper.
- Modify `tests/fixtures/sample-paper/main.tex`: enrich the fixture with abstract and preamble material needed by mapper tests.
- Modify `tests/fixtures/sample-paper/sections/introduction.tex`: keep existing section/caption coverage and add one protected environment if needed.
- Create or modify `tests/test_project_map.py`: assert source-map fields, protected regions, and that preamble is not treated as a normal section task.
- Create `tests/test_build_task_skeleton.py`: assert task skeleton schema and section-oriented task generation.
- Create `tests/test_real_paper_readonly.py`: optional read-only validation against `/data/proj/icml2026/ICML2026`, skipped if that path is absent.
- Modify `tests/test_inspect_latex_project.py` and `tests/test_smoke_workflow.py` only as needed to preserve backward compatibility.

## Task 0: Baseline Verification

**Files:**
- Read: `docs/superpowers/specs/2026-05-15-model-led-task-decomposition-design.md`
- Read: `architecture.md`

- [ ] **Step 1: Verify current baseline tests**

Run:

```bash
pytest -q
```

Expected: all current tests pass.

- [ ] **Step 2: Confirm working tree state**

Run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher status --short
```

Expected: no tracked or untracked work other than ignored caches.

## Task 1: Task Protocol Reference

**Files:**
- Create: `references/task-protocol.md`
- Modify: `architecture.md`
- Modify: `references/knowledge.md`

- [ ] **Step 1: Write `references/task-protocol.md`**

Create the file with:

```markdown
# Task Protocol

This document defines the model-led task plan and specialist-agent output schemas.

## Project Map Boundary

The project map is mechanical. It may describe files, anchors, labels, references, citations, captions, and protected regions. It must not decide which prose units should be polished.

## Main-Agent Task Plan

The main agent creates and owns the task plan after reading the paper context.

Each task is a JSON object with:

```json
{
  "id": "introduction-section-polish",
  "type": "section_polish",
  "title": "Polish Introduction",
  "target_files": ["src/1_introduction.tex"],
  "anchors": [{"file": "src/1_introduction.tex", "line": 1, "kind": "section", "title": "Introduction"}],
  "status": "pending",
  "assigned_role": "section_polisher",
  "required_context": ["paper thesis", "section role", "terminology", "latex preservation rules"],
  "acceptance_check": "User approves final wording and validator reports no LaTeX construct damage."
}
```

Valid task types:

- `macro_review`
- `section_polish`
- `caption_polish`
- `terminology_check`
- `latex_safety_check`
- `cjk_fullwidth_scan`

Valid statuses:

- `pending`
- `in_progress`
- `blocked`
- `review_ready`
- `user_approved`
- `completed`

## Specialist-Agent Output

Specialist agents return suggestions only. They must not edit files, commit, push, or update logs.

Each output is a JSON object with:

```json
{
  "task_id": "introduction-section-polish",
  "target": {"file": "src/1_introduction.tex", "line_range": [1, 30]},
  "original_text": "Original source excerpt.",
  "proposed_text": "Suggested revision.",
  "rationale": ["Reason for the change."],
  "latex_constructs_preserved": ["\\\\citep{...}", "Figure~\\\\ref{fig:...}"],
  "risks": [],
  "questions": []
}
```

The main agent reviews specialist output before presenting final text to the user.
```

- [ ] **Step 2: Update `architecture.md`**

In the `References` section, add:

```markdown
- `references/task-protocol.md`: Task plan and specialist-agent output schemas for model-led decomposition.
```

In `File Placement Rules`, add:

```markdown
- Put shared task and agent-output protocols in `references/`, not in scripts.
```

- [ ] **Step 3: Update `references/knowledge.md`**

Add to confirmed preferences:

```markdown
- Python helpers should not own semantic paragraph splitting. They should provide source maps and validation only; the main agent should decompose polishing tasks after reading the paper.
```

- [ ] **Step 4: Commit Task 1**

Run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher add references/task-protocol.md architecture.md references/knowledge.md
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher commit -m "docs: add model-led task protocol"
```

## Task 2: Project Map Output

**Files:**
- Modify: `scripts/inspect_latex_project.py`
- Modify: `tests/fixtures/sample-paper/main.tex`
- Modify: `tests/fixtures/sample-paper/sections/introduction.tex`
- Create: `tests/test_project_map.py`
- Modify: `tests/test_inspect_latex_project.py` only if compatibility adjustments are required.

- [ ] **Step 1: Write failing project-map tests**

Create `tests/test_project_map.py`:

```python
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PROJECT = ROOT / "fixtures" / "sample-paper"
SCRIPT = ROOT.parent / "scripts" / "inspect_latex_project.py"


def run_mapper():
    result = subprocess.run(
        ["python", str(SCRIPT), "--map", str(PROJECT)],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def test_project_map_contains_mechanical_source_fields():
    data = run_mapper()
    assert data["schema_version"] == 2
    assert data["mode"] == "project_map"
    assert data["main_file"] == "main.tex"
    assert "sections/introduction.tex" in data["files"]
    assert data["sections"][0]["title"] == "Introduction"
    assert data["sections"][0]["anchor"]["file"] == "sections/introduction.tex"


def test_project_map_separates_captions_labels_refs_and_citations():
    data = run_mapper()
    assert any(item["key"] == "fig:overview" for item in data["labels"])
    assert any(item["key"] == "smith2020" for item in data["citations"])
    assert any(item["label"] == "fig:overview" for item in data["captions"])


def test_project_map_marks_preamble_as_protected_not_section_task():
    data = run_mapper()
    protected = data["protected_regions"]
    assert any(region["kind"] == "preamble" and region["file"] == "main.tex" for region in protected)
    assert all(section["file"] != "main.tex" for section in data["sections"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
pytest tests/test_project_map.py -q
```

Expected: FAIL because `--map` mode and schema-version-2 fields do not exist.

- [ ] **Step 3: Extend `scripts/inspect_latex_project.py`**

Add a `--map PROJECT_DIR` CLI mode while preserving the existing `PROJECT_DIR` behavior for current tests.

Required implementation details:

```python
def build_project_map(project: Path) -> dict:
    project = project.resolve()
    main = find_main_file(project)
    files = expand_files(project, main)
    sections: list[dict] = []
    captions: list[dict] = []
    labels: list[dict] = []
    refs: list[dict] = []
    citations: list[dict] = []
    protected_regions: list[dict] = []

    for path in files:
        rel = path.relative_to(project).as_posix()
        text = read_text(path)
        protected_regions.extend(detect_protected_regions(rel, text))
        sections.extend(extract_sections(rel, text))
        captions.extend(extract_captions(rel, text))
        labels.extend(extract_keyed_constructs(rel, text, LABEL_RE, "label"))
        refs.extend(extract_multi_keyed_constructs(rel, text, REF_RE, "ref"))
        citations.extend(extract_multi_keyed_constructs(rel, text, CITE_RE, "citation"))

    return {
        "schema_version": 2,
        "mode": "project_map",
        "project_root": str(project),
        "main_file": main.relative_to(project).as_posix(),
        "files": [path.relative_to(project).as_posix() for path in files],
        "sections": sections,
        "captions": captions,
        "labels": labels,
        "refs": refs,
        "citations": citations,
        "protected_regions": protected_regions,
    }
```

Add helper functions with these exact responsibilities:

```python
def make_anchor(file: str, line: int, kind: str, title: str | None = None) -> dict:
    anchor = {"file": file, "line": line, "kind": kind}
    if title is not None:
        anchor["title"] = title
    return anchor
```

```python
def extract_sections(file: str, text: str) -> list[dict]:
    sections = []
    for match in SECTION_RE.finditer(text):
        line = line_number(text, match.start())
        sections.append({
            "level": match.group(1),
            "title": match.group(2),
            "file": file,
            "line": line,
            "anchor": make_anchor(file, line, "section", match.group(2)),
        })
    return sections
```

```python
def extract_captions(file: str, text: str) -> list[dict]:
    captions = []
    for match in CAPTION_RE.finditer(text):
        line = line_number(text, match.start())
        nearby = text[match.end(): match.end() + 300]
        label_match = LABEL_RE.search(nearby)
        captions.append({
            "file": file,
            "line": line,
            "text": match.group(1).strip(),
            "label": label_match.group(1) if label_match else None,
            "anchor": make_anchor(file, line, "caption"),
        })
    return captions
```

```python
def detect_protected_regions(file: str, text: str) -> list[dict]:
    regions = []
    begin_doc = text.find("\\begin{document}")
    if begin_doc > 0:
        regions.append({
            "file": file,
            "kind": "preamble",
            "start_line": 1,
            "end_line": line_number(text, begin_doc),
            "reason": "LaTeX preamble is not a polishing task.",
        })
    for env in ("table", "tabular", "rawbox", "algorithm", "align", "equation"):
        pattern = re.compile(rf"\\begin\{{{env}\}}.*?\\end\{{{env}\}}", re.DOTALL)
        for match in pattern.finditer(text):
            regions.append({
                "file": file,
                "kind": f"environment:{env}",
                "start_line": line_number(text, match.start()),
                "end_line": line_number(text, match.end()),
                "reason": f"{env} environment should not be treated as ordinary prose.",
            })
    return regions
```

Add keyed construct helpers:

```python
def extract_keyed_constructs(file: str, text: str, pattern: re.Pattern, kind: str) -> list[dict]:
    return [
        {"file": file, "line": line_number(text, match.start()), "kind": kind, "key": match.group(1)}
        for match in pattern.finditer(text)
    ]
```

```python
def extract_multi_keyed_constructs(file: str, text: str, pattern: re.Pattern, kind: str) -> list[dict]:
    items = []
    for match in pattern.finditer(text):
        for key in match.group(1).split(","):
            key = key.strip()
            if key:
                items.append({"file": file, "line": line_number(text, match.start()), "kind": kind, "key": key})
    return items
```

Update `main()` so:

```python
if len(argv) == 3 and argv[1] == "--map":
    print(json.dumps(build_project_map(Path(argv[2])), ensure_ascii=False, indent=2))
    return 0
if len(argv) == 2:
    data = inspect(Path(argv[1]))
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0
print("usage: inspect_latex_project.py [--map] PROJECT_DIR", file=sys.stderr)
return 2
```

- [ ] **Step 4: Run project-map tests**

Run:

```bash
pytest tests/test_project_map.py -q
```

Expected: PASS.

- [ ] **Step 5: Run compatibility tests**

Run:

```bash
pytest tests/test_inspect_latex_project.py tests/test_smoke_workflow.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit Task 2**

Run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher add scripts/inspect_latex_project.py tests/test_project_map.py tests/test_inspect_latex_project.py tests/test_smoke_workflow.py tests/fixtures/sample-paper/main.tex tests/fixtures/sample-paper/sections/introduction.tex
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher commit -m "feat: add project map mode"
```

## Task 3: Mechanical Task Skeleton Builder

**Files:**
- Create: `scripts/build_task_skeleton.py`
- Create: `tests/test_build_task_skeleton.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_build_task_skeleton.py`:

```python
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
MAPPER = ROOT.parent / "scripts" / "inspect_latex_project.py"
SCRIPT = ROOT.parent / "scripts" / "build_task_skeleton.py"
PROJECT = ROOT / "fixtures" / "sample-paper"


def test_builds_section_oriented_task_skeleton(tmp_path):
    map_path = tmp_path / "project-map.json"
    task_path = tmp_path / "tasks.json"
    mapped = subprocess.run(
        ["python", str(MAPPER), "--map", str(PROJECT)],
        check=True,
        text=True,
        capture_output=True,
    )
    map_path.write_text(mapped.stdout, encoding="utf-8")

    subprocess.run(["python", str(SCRIPT), str(map_path), str(task_path)], check=True)

    data = json.loads(task_path.read_text(encoding="utf-8"))
    task_types = [task["type"] for task in data["tasks"]]
    assert data["schema_version"] == 1
    assert "macro_review" in task_types
    assert "section_polish" in task_types
    assert "caption_polish" in task_types
    assert "cjk_fullwidth_scan" in task_types
    assert all(task["status"] == "pending" for task in data["tasks"])


def test_task_skeleton_is_mechanical_not_final_agent_plan(tmp_path):
    map_path = tmp_path / "project-map.json"
    task_path = tmp_path / "tasks.json"
    mapped = subprocess.run(
        ["python", str(MAPPER), "--map", str(PROJECT)],
        check=True,
        text=True,
        capture_output=True,
    )
    map_path.write_text(mapped.stdout, encoding="utf-8")

    subprocess.run(["python", str(SCRIPT), str(map_path), str(task_path)], check=True)

    data = json.loads(task_path.read_text(encoding="utf-8"))
    assert data["mode"] == "mechanical_task_skeleton"
    assert data["requires_main_agent_review"] is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
pytest tests/test_build_task_skeleton.py -q
```

Expected: FAIL because `scripts/build_task_skeleton.py` does not exist.

- [ ] **Step 3: Implement `scripts/build_task_skeleton.py`**

Create the script:

```python
#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return value or "untitled"


def make_task(task_id: str, task_type: str, title: str, target_files: list[str], anchors: list[dict], assigned_role: str, acceptance_check: str) -> dict:
    return {
        "id": task_id,
        "type": task_type,
        "title": title,
        "target_files": target_files,
        "anchors": anchors,
        "status": "pending",
        "assigned_role": assigned_role,
        "required_context": ["paper thesis", "section role", "terminology", "latex preservation rules"],
        "acceptance_check": acceptance_check,
    }


def build(project_map: dict) -> dict:
    tasks = [
        make_task(
            "macro-review",
            "macro_review",
            "Paper-level reviewer diagnosis",
            project_map["files"],
            [],
            "macro_reviewer",
            "User confirms the macro optimization direction before polishing begins.",
        ),
        make_task(
            "terminology-check",
            "terminology_check",
            "Terminology consistency pass",
            project_map["files"],
            [],
            "terminology_checker",
            "Main agent records stable terminology decisions in references/knowledge.md.",
        ),
        make_task(
            "cjk-fullwidth-scan",
            "cjk_fullwidth_scan",
            "Chinese and full-width punctuation scan",
            project_map["files"],
            [],
            "latex_safety_checker",
            "All flagged characters are reviewed before any source writeback.",
        ),
        make_task(
            "latex-safety-check",
            "latex_safety_check",
            "LaTeX safety review",
            project_map["files"],
            [],
            "latex_safety_checker",
            "No specialist output is accepted if it damages LaTeX constructs.",
        ),
    ]

    for section in project_map.get("sections", []):
        title = section["title"]
        tasks.append(make_task(
            f"{slug(title)}-section-polish",
            "section_polish",
            f"Polish {title}",
            [section["file"]],
            [section["anchor"]],
            "section_polisher",
            "User approves final section wording and validator reports no LaTeX construct damage.",
        ))

    for index, caption in enumerate(project_map.get("captions", []), start=1):
        label = caption.get("label") or f"caption-{index}"
        tasks.append(make_task(
            f"{slug(label)}-caption-polish",
            "caption_polish",
            f"Polish caption {label}",
            [caption["file"]],
            [caption["anchor"]],
            "caption_polisher",
            "Caption remains semantically consistent with surrounding text and preserved labels.",
        ))

    return {
        "schema_version": 1,
        "mode": "mechanical_task_skeleton",
        "requires_main_agent_review": True,
        "project_root": project_map["project_root"],
        "main_file": project_map["main_file"],
        "tasks": tasks,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: build_task_skeleton.py PROJECT_MAP_JSON OUTPUT_JSON", file=sys.stderr)
        return 2
    project_map = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    Path(argv[2]).write_text(json.dumps(build(project_map), ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 4: Run task skeleton tests**

Run:

```bash
pytest tests/test_build_task_skeleton.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit Task 3**

Run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher add scripts/build_task_skeleton.py tests/test_build_task_skeleton.py
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher commit -m "feat: add mechanical task skeleton builder"
```

## Task 4: Skill Workflow And Architecture Sync

**Files:**
- Modify: `SKILL.md`
- Modify: `architecture.md`
- Modify: `references/knowledge.md`

- [ ] **Step 1: Update `SKILL.md` workflow**

Replace the current Core Workflow with a model-led workflow:

```markdown
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
```

Update Defaults:

```markdown
- Task decomposition: model-led by the main agent after reading project context.
- Helper scripts: mechanical source mapping, workbench generation, logging, and validation only.
```

Add reference:

```markdown
- Task and specialist-agent protocol: `references/task-protocol.md`
```

- [ ] **Step 2: Update `architecture.md` script list**

Add:

```markdown
- `scripts/build_task_skeleton.py`: Generates a mechanical starter task skeleton from a project map. The skeleton requires main-agent review before use.
```

Adjust `scripts/inspect_latex_project.py` description to mention `--map`.

- [ ] **Step 3: Update `references/knowledge.md`**

Add:

```markdown
- Specialist agents are suggestion-only by default. The main agent keeps exclusive writeback authority and reviews all suggestions before presenting final text to the user.
```

- [ ] **Step 4: Run tests**

Run:

```bash
pytest -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit Task 4**

Run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher add SKILL.md architecture.md references/knowledge.md
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher commit -m "docs: update skill for model-led workflow"
```

## Task 5: Read-Only Real Paper Validation

**Files:**
- Create: `tests/test_real_paper_readonly.py`

- [ ] **Step 1: Write read-only integration test**

Create `tests/test_real_paper_readonly.py`:

```python
import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).parent
PROJECT = Path("/data/proj/icml2026/ICML2026")
MAPPER = ROOT.parent / "scripts" / "inspect_latex_project.py"
TASKER = ROOT.parent / "scripts" / "build_task_skeleton.py"


pytestmark = pytest.mark.skipif(not PROJECT.exists(), reason="real ICML paper fixture is not available")


def snapshot_mtimes(project: Path) -> dict[str, int]:
    return {
        str(path.relative_to(project)): path.stat().st_mtime_ns
        for path in project.rglob("*")
        if path.is_file()
    }


def test_real_icml_project_mapping_is_read_only(tmp_path):
    before = snapshot_mtimes(PROJECT)
    map_path = tmp_path / "icml-project-map.json"
    task_path = tmp_path / "icml-task-skeleton.json"

    mapped = subprocess.run(
        ["python", str(MAPPER), "--map", str(PROJECT)],
        check=True,
        text=True,
        capture_output=True,
    )
    map_path.write_text(mapped.stdout, encoding="utf-8")
    subprocess.run(["python", str(TASKER), str(map_path), str(task_path)], check=True)

    after = snapshot_mtimes(PROJECT)
    assert after == before

    project_map = json.loads(map_path.read_text(encoding="utf-8"))
    tasks = json.loads(task_path.read_text(encoding="utf-8"))
    assert project_map["main_file"] == "example_paper.tex"
    assert "src/1_introduction.tex" in project_map["files"]
    assert any(section["title"] == "Introduction" for section in project_map["sections"])
    assert any(task["type"] == "section_polish" and "Introduction" in task["title"] for task in tasks["tasks"])
    assert tasks["requires_main_agent_review"] is True
```

- [ ] **Step 2: Run read-only test**

Run:

```bash
pytest tests/test_real_paper_readonly.py -q
```

Expected: PASS when `/data/proj/icml2026/ICML2026` exists; SKIPPED otherwise. The test writes only to pytest `tmp_path`.

- [ ] **Step 3: Run full test suite**

Run:

```bash
pytest -q
```

Expected: all tests pass.

- [ ] **Step 4: Commit Task 5**

Run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher add tests/test_real_paper_readonly.py
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher commit -m "test: add read-only real paper validation"
```

## Task 6: Final Verification And Push

**Files:**
- Modify only if earlier tasks reveal a plan/docs mismatch:
  - `docs/superpowers/specs/2026-05-15-model-led-task-decomposition-design.md`
  - `docs/superpowers/plans/2026-05-15-model-led-task-decomposition.md`
  - `architecture.md`

- [ ] **Step 1: Run final tests**

Run:

```bash
pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Generate sample project map and task skeleton to `/tmp`**

Run:

```bash
python scripts/inspect_latex_project.py --map tests/fixtures/sample-paper > /tmp/latex-paper-polisher-project-map.json
python scripts/build_task_skeleton.py /tmp/latex-paper-polisher-project-map.json /tmp/latex-paper-polisher-task-skeleton.json
```

Expected: both files are written under `/tmp`.

- [ ] **Step 3: Inspect generated task skeleton**

Run:

```bash
python -m json.tool /tmp/latex-paper-polisher-task-skeleton.json
```

Expected: output includes `macro_review`, `section_polish`, `caption_polish`, `terminology_check`, `latex_safety_check`, and `cjk_fullwidth_scan`.

- [ ] **Step 4: Verify no runtime artifacts are tracked**

Run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher status --ignored --short
```

Expected: ignored caches may appear; no `.latex-paper-polisher/logs/` or generated `/tmp` artifacts are tracked.

- [ ] **Step 5: Commit plan/docs adjustments if any**

If earlier execution required corrections to docs or this plan, run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher add docs/superpowers/specs/2026-05-15-model-led-task-decomposition-design.md docs/superpowers/plans/2026-05-15-model-led-task-decomposition.md architecture.md
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher commit -m "docs: align model-led decomposition plan"
```

If no docs changed, skip this commit.

- [ ] **Step 6: Push commits**

Run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher push
```

Expected: all local commits are pushed to `origin/main`.

## Self-Review Notes

- Spec coverage: project map, main-agent ownership, specialist suggestion-only protocol, task plan schema, real-paper read-only validation, and centralized writeback are all mapped to tasks.
- Red-flag scan: no forbidden marker terms or unspecified implementation steps remain.
- Type consistency: task fields match `references/task-protocol.md`, `build_task_skeleton.py`, and tests.
