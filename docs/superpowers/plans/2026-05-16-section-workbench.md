# Section Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first section-level browser workbench that loads precomputed section polishing suggestions, lets the user navigate paragraphs locally, manually maintain final text, and download section-final-edits JSON without modifying source files.

**Architecture:** Python scripts remain deterministic artifact generators and validators. Reusable browser assets live under `assets/workbench/`; generated paper-specific HTML and JSON remain outside the repository, typically under `/data/latex_test`. Model-generated paper summary and section polish content are represented as local JSON schemas so later agent steps can produce them consistently.

**Tech Stack:** Python 3 standard library, pytest, static HTML/CSS/JavaScript, JSON artifacts, existing Codex skill layout.

---

## File Structure

- Modify `references/task-protocol.md`: Add formal schemas for `paper_summary`, `section_polish_package`, and `section_final_edits`.
- Modify `architecture.md`: Document section workbench helper scripts and runtime artifacts.
- Modify `references/knowledge.md`: Record the section workbench workflow preference.
- Create `tests/fixtures/section-workbench/paper-summary.json`: Minimal paper summary fixture.
- Create `tests/fixtures/section-workbench/section-polish-package-introduction.json`: Minimal section package fixture with two paragraph items.
- Create `scripts/validate_section_polish_package.py`: Validate section package schema and enforce `editable_text == original_text` by default.
- Create `tests/test_section_polish_package.py`: Tests for section package validation.
- Create `scripts/build_section_workbench.py`: Generate section workbench HTML from a section package.
- Modify `assets/workbench/workbench.html`: Support a section browser layout.
- Modify `assets/workbench/workbench.css`: Style section navigation, copy buttons, final text, notes, and discussion panels.
- Modify `assets/workbench/workbench.js`: Add local section navigation, copy buttons, editable text memory, discussion transcript memory, and section-final-edits download.
- Create `tests/test_build_section_workbench.py`: Tests for generated section workbench HTML.
- Modify `tests/test_build_workbench.py` only if reusable asset changes require compatibility adjustments.

## Task 1: Protocol And Fixtures

**Files:**
- Modify: `references/task-protocol.md`
- Modify: `architecture.md`
- Modify: `references/knowledge.md`
- Create: `tests/fixtures/section-workbench/paper-summary.json`
- Create: `tests/fixtures/section-workbench/section-polish-package-introduction.json`

- [ ] **Step 1: Create paper summary fixture**

Create `tests/fixtures/section-workbench/paper-summary.json`:

```json
{
  "schema_version": 1,
  "mode": "paper_summary",
  "project_root": "/example/paper",
  "main_file": "main.tex",
  "thesis": "The paper studies robust small-model distillation.",
  "contributions": [
    "Identifies a quality-utility mismatch.",
    "Shows that style alignment improves downstream utility."
  ],
  "section_map": [
    {
      "section_id": "introduction",
      "title": "Introduction",
      "source_file": "sections/introduction.tex",
      "role": "Motivates the problem and states contributions."
    }
  ],
  "terminology": [
    "Small Language Models",
    "Quality-Utility Paradox",
    "Style-Aligned Refinement"
  ],
  "macro_risks": [
    "Avoid overstating evidence before experiments are introduced."
  ],
  "structural_suggestions": [
    "Keep the contribution list aligned with later experiments."
  ],
  "polishing_guidance": [
    "Preserve LaTeX citations, labels, refs, and math.",
    "Prefer precise academic English over stronger claims."
  ]
}
```

- [ ] **Step 2: Create section polish package fixture**

Create `tests/fixtures/section-workbench/section-polish-package-introduction.json`:

```json
{
  "schema_version": 1,
  "mode": "section_polish_package",
  "section_id": "introduction",
  "section_title": "Introduction",
  "source_file": "sections/introduction.tex",
  "paper_summary_ref": "paper-summary.json",
  "items": [
    {
      "item_id": "intro-p001",
      "source_file": "sections/introduction.tex",
      "line_range": [4, 4],
      "original_text": "Prior work has studied this topic~\\cite{smith2020}. However, existing methods are often limited when $n$ is large.",
      "suggested_text": "Prior work has examined this topic~\\cite{smith2020}. However, existing methods remain limited when $n$ is large.",
      "revision_notes": [
        "Replaces a generic verb with a more academic one.",
        "Keeps the citation and inline math unchanged."
      ],
      "risks": [],
      "questions": [],
      "editable_text": "Prior work has studied this topic~\\cite{smith2020}. However, existing methods are often limited when $n$ is large."
    },
    {
      "item_id": "intro-p002",
      "source_file": "sections/introduction.tex",
      "line_range": [6, 6],
      "original_text": "We propose a compact method that improves robustness.",
      "suggested_text": "We propose a compact method that improves robustness while preserving computational efficiency.",
      "revision_notes": [
        "Adds a more specific benefit for the proposed method."
      ],
      "risks": [
        "Confirm that computational efficiency is supported by later experiments."
      ],
      "questions": [
        "Should this paragraph preview the main contribution list?"
      ],
      "editable_text": "We propose a compact method that improves robustness."
    }
  ]
}
```

- [ ] **Step 3: Update task protocol**

Add these sections to `references/task-protocol.md` after `## Project Map Boundary`:

```markdown
## Paper Summary

A paper summary is generated after the main agent reads the full paper. It captures paper-level understanding for later section and paragraph agents.

Required fields:

```json
{
  "schema_version": 1,
  "mode": "paper_summary",
  "project_root": "/path/to/paper",
  "main_file": "main.tex",
  "thesis": "Main paper claim.",
  "contributions": [],
  "section_map": [],
  "terminology": [],
  "macro_risks": [],
  "structural_suggestions": [],
  "polishing_guidance": []
}
```

Paper summaries are context artifacts and do not authorize source edits.

## Section Polish Package

A section polish package is generated after an agent reads one full section plus the paper summary and needed neighboring context.

Required fields:

```json
{
  "schema_version": 1,
  "mode": "section_polish_package",
  "section_id": "introduction",
  "section_title": "Introduction",
  "source_file": "src/1_introduction.tex",
  "paper_summary_ref": "paper-summary.json",
  "items": [
    {
      "item_id": "intro-p001",
      "source_file": "src/1_introduction.tex",
      "line_range": [10, 18],
      "original_text": "Original paragraph.",
      "suggested_text": "Suggested revision.",
      "revision_notes": ["Why this change helps."],
      "risks": [],
      "questions": [],
      "editable_text": "Original paragraph."
    }
  ]
}
```

`editable_text` must default to `original_text`. The suggested text is not automatically adopted.

## Section Final Edits

The section workbench downloads section-final-edits JSON after the user reviews the whole section.

Required fields:

```json
{
  "schema_version": 1,
  "mode": "section_final_edits",
  "section_id": "introduction",
  "section_title": "Introduction",
  "items": [
    {
      "item_id": "intro-p001",
      "source_file": "src/1_introduction.tex",
      "line_range": [10, 18],
      "original_text": "Original paragraph.",
      "final_text": "User-maintained final paragraph."
    }
  ]
}
```

Section final edits are staging artifacts. They do not modify source files.
```

- [ ] **Step 4: Update architecture**

In `architecture.md`, add to `Helper Scripts`:

```markdown
- `scripts/validate_section_polish_package.py`: Validates section polish package JSON before generating a section workbench.
- `scripts/build_section_workbench.py`: Generates an interactive section-level HTML workbench from a section polish package.
```

In `Local-Only Runtime Artifacts`, add:

```markdown
- Paper summary, section polish package, section final edits, and generated section workbench HTML under `/data/latex_test/` or another runtime output directory.
```

- [ ] **Step 5: Update knowledge**

Add to `references/knowledge.md` confirmed preferences:

```markdown
- Section polishing should use a precomputed section package so previous/next paragraph navigation is local and fast. The editable text defaults to original text, with original/suggested copy buttons for manual editing.
```

- [ ] **Step 6: Commit protocol fixtures**

Run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher add references/task-protocol.md architecture.md references/knowledge.md tests/fixtures/section-workbench/paper-summary.json tests/fixtures/section-workbench/section-polish-package-introduction.json
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher commit -m "docs: add section workbench protocols"
```

Expected: commit succeeds.

## Task 2: Section Package Validator

**Files:**
- Create: `scripts/validate_section_polish_package.py`
- Create: `tests/test_section_polish_package.py`

- [ ] **Step 1: Write failing validator tests**

Create `tests/test_section_polish_package.py`:

```python
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
FIXTURE = ROOT / "fixtures" / "section-workbench" / "section-polish-package-introduction.json"
SCRIPT = ROOT.parent / "scripts" / "validate_section_polish_package.py"


def test_valid_section_polish_package_passes():
    result = subprocess.run(
        ["python", str(SCRIPT), str(FIXTURE)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    summary = json.loads(result.stdout)
    assert summary["ok"] is True
    assert summary["section_id"] == "introduction"
    assert summary["item_count"] == 2
    assert summary["errors"] == []


def test_rejects_editable_text_that_does_not_default_to_original(tmp_path):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["items"][0]["editable_text"] = data["items"][0]["suggested_text"]
    path = tmp_path / "bad-package.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(
        ["python", str(SCRIPT), str(path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert summary["ok"] is False
    assert "items[0].editable_text must equal original_text by default" in summary["errors"]


def test_rejects_missing_required_item_field(tmp_path):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    del data["items"][1]["revision_notes"]
    path = tmp_path / "bad-package.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    result = subprocess.run(
        ["python", str(SCRIPT), str(path)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert "items[1] missing required field: revision_notes" in summary["errors"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
pytest tests/test_section_polish_package.py -q
```

Expected: FAIL because `scripts/validate_section_polish_package.py` does not exist.

- [ ] **Step 3: Implement validator**

Create `scripts/validate_section_polish_package.py`:

```python
#!/usr/bin/env python3
import json
import sys
from pathlib import Path


PACKAGE_FIELDS = {
    "schema_version",
    "mode",
    "section_id",
    "section_title",
    "source_file",
    "paper_summary_ref",
    "items",
}

ITEM_FIELDS = {
    "item_id",
    "source_file",
    "line_range",
    "original_text",
    "suggested_text",
    "revision_notes",
    "risks",
    "questions",
    "editable_text",
}


def validate_item(item: dict, index: int) -> list[str]:
    errors = []
    for field in sorted(ITEM_FIELDS - item.keys()):
        errors.append(f"items[{index}] missing required field: {field}")
    if item.get("editable_text") != item.get("original_text"):
        errors.append(f"items[{index}].editable_text must equal original_text by default")
    for field in ("revision_notes", "risks", "questions"):
        if field in item and not isinstance(item[field], list):
            errors.append(f"items[{index}].{field} must be a list")
    line_range = item.get("line_range")
    if line_range is not None and (
        not isinstance(line_range, list)
        or len(line_range) != 2
        or not all(isinstance(value, int) for value in line_range)
    ):
        errors.append(f"items[{index}].line_range must be a two-integer list")
    return errors


def validate(package: dict) -> dict:
    errors = []
    for field in sorted(PACKAGE_FIELDS - package.keys()):
        errors.append(f"missing required field: {field}")
    if package.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if package.get("mode") != "section_polish_package":
        errors.append("mode must be section_polish_package")
    items = package.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty list")
    elif isinstance(items, list):
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"items[{index}] must be an object")
            else:
                errors.extend(validate_item(item, index))
    return {
        "ok": not errors,
        "section_id": package.get("section_id"),
        "item_count": len(items) if isinstance(items, list) else 0,
        "errors": errors,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_section_polish_package.py SECTION_PACKAGE_JSON", file=sys.stderr)
        return 2
    package = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    summary = validate(package)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 4: Run validator tests**

Run:

```bash
pytest tests/test_section_polish_package.py -q
```

Expected: PASS.

- [ ] **Step 5: Run full tests**

Run:

```bash
pytest -q
```

Expected: all tests pass.

- [ ] **Step 6: Commit validator**

Run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher add scripts/validate_section_polish_package.py tests/test_section_polish_package.py
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher commit -m "feat: validate section polish packages"
```

Expected: commit succeeds.

## Task 3: Section Workbench HTML Generator

**Files:**
- Create: `scripts/build_section_workbench.py`
- Modify: `assets/workbench/workbench.html`
- Modify: `assets/workbench/workbench.css`
- Modify: `assets/workbench/workbench.js`
- Create: `tests/test_build_section_workbench.py`

- [ ] **Step 1: Write failing section workbench tests**

Create `tests/test_build_section_workbench.py`:

```python
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PACKAGE = ROOT / "fixtures" / "section-workbench" / "section-polish-package-introduction.json"
SCRIPT = ROOT.parent / "scripts" / "build_section_workbench.py"


def test_builds_section_workbench_html(tmp_path):
    output_path = tmp_path / "section-workbench.html"

    subprocess.run(["python", str(SCRIPT), str(PACKAGE), str(output_path)], check=True)

    html = output_path.read_text(encoding="utf-8")
    assert "Section Workbench" in html
    assert "Introduction" in html
    assert "intro-p001" in html
    assert "Previous Paragraph" in html
    assert "Next Paragraph" in html
    assert "Submit Whole Section" in html
    assert "copy-original" in html
    assert "copy-suggested" in html
    assert "final-text" in html
    assert "agent-discussion" in html
    assert "downloadSectionFinalEdits" in html
    assert "section-polish-package" in html


def test_section_workbench_embeds_package_json_safely(tmp_path):
    output_path = tmp_path / "section-workbench.html"

    subprocess.run(["python", str(SCRIPT), str(PACKAGE), str(output_path)], check=True)

    html = output_path.read_text(encoding="utf-8")
    assert '<script id="section-polish-package" type="application/json">' in html
    assert "\\u003c" not in html
    assert "editable_text" in html
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
pytest tests/test_build_section_workbench.py -q
```

Expected: FAIL because `scripts/build_section_workbench.py` does not exist.

- [ ] **Step 3: Add section template asset**

Append this section-specific markup to `assets/workbench/workbench.html` by replacing the existing body with a template that supports both paragraph and section payloads is too broad. Instead create a separate section template file `assets/workbench/section-workbench.html` with:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Section Workbench</title>
  <style>
__WORKBENCH_CSS__
  </style>
</head>
<body data-workbench-mode="section">
<main>
  <header class="section-header">
    <h1>Section Workbench</h1>
    <div class="meta">__SECTION_TITLE__ · <span id="item-counter"></span> · <span id="source-location"></span></div>
  </header>

  <div class="grid">
    <section>
      <div class="panel-title">
        <h2>Original</h2>
        <button id="copy-original" type="button">Copy</button>
      </div>
      <pre id="original-text"></pre>
    </section>
    <section>
      <div class="panel-title">
        <h2>Suggested Revision</h2>
        <button id="copy-suggested" type="button">Copy</button>
      </div>
      <pre id="suggested-text"></pre>
    </section>
    <section class="full">
      <h2>Revision Notes</h2>
      <ol id="revision-notes"></ol>
    </section>
    <section>
      <h2>Risks</h2>
      <ul id="risks" class="warning"></ul>
    </section>
    <section>
      <h2>Questions</h2>
      <ul id="questions"></ul>
    </section>
    <section class="full">
      <h2>Final Text</h2>
      <textarea id="final-text" rows="10"></textarea>
      <div class="decision-actions">
        <button id="previous-item" type="button">Previous Paragraph</button>
        <button id="next-item" type="button">Next Paragraph</button>
        <button id="submit-section" type="button">Submit Whole Section</button>
      </div>
    </section>
    <section class="full">
      <h2>Polishing Agent Discussion</h2>
      <textarea id="agent-discussion" rows="5" placeholder="Discuss the current paragraph with the polishing agent. This does not automatically change final text."></textarea>
    </section>
    <section class="full">
      <h2>Section Final Edits JSON</h2>
      <pre id="section-final-edits">{}</pre>
    </section>
  </div>
  <script id="section-polish-package" type="application/json">__SECTION_PACKAGE_JSON__</script>
  <script>
__SECTION_WORKBENCH_JS__
  </script>
</main>
</body>
</html>
```

- [ ] **Step 4: Add section JavaScript asset**

Create `assets/workbench/section-workbench.js`:

```javascript
const sectionPackage = JSON.parse(document.getElementById("section-polish-package").textContent);
let currentIndex = 0;
const finalTexts = {};
const discussions = {};

function currentItem() {
  return sectionPackage.items[currentIndex];
}

function listItems(elementId, values, ordered = false) {
  const element = document.getElementById(elementId);
  element.innerHTML = "";
  if (!values || values.length === 0) {
    const item = document.createElement("li");
    item.textContent = "None.";
    element.appendChild(item);
    return;
  }
  values.forEach((value) => {
    const item = document.createElement("li");
    item.textContent = value;
    element.appendChild(item);
  });
}

function saveCurrentState() {
  const item = currentItem();
  finalTexts[item.item_id] = document.getElementById("final-text").value;
  discussions[item.item_id] = document.getElementById("agent-discussion").value;
}

function loadCurrentItem() {
  const item = currentItem();
  document.getElementById("item-counter").textContent = `${currentIndex + 1} / ${sectionPackage.items.length}`;
  document.getElementById("source-location").textContent = `${item.source_file}:${item.line_range[0]}-${item.line_range[1]}`;
  document.getElementById("original-text").textContent = item.original_text;
  document.getElementById("suggested-text").textContent = item.suggested_text;
  listItems("revision-notes", item.revision_notes, true);
  listItems("risks", item.risks);
  listItems("questions", item.questions);
  document.getElementById("final-text").value = finalTexts[item.item_id] ?? item.editable_text ?? item.original_text;
  document.getElementById("agent-discussion").value = discussions[item.item_id] ?? "";
}

function copyText(elementId) {
  const text = document.getElementById(elementId).textContent;
  navigator.clipboard.writeText(text);
}

function goTo(delta) {
  saveCurrentState();
  currentIndex = Math.max(0, Math.min(sectionPackage.items.length - 1, currentIndex + delta));
  loadCurrentItem();
}

function buildFinalEdits() {
  saveCurrentState();
  return {
    schema_version: 1,
    mode: "section_final_edits",
    section_id: sectionPackage.section_id,
    section_title: sectionPackage.section_title,
    items: sectionPackage.items.map((item) => ({
      item_id: item.item_id,
      source_file: item.source_file,
      line_range: item.line_range,
      original_text: item.original_text,
      final_text: finalTexts[item.item_id] ?? item.editable_text ?? item.original_text
    }))
  };
}

function downloadSectionFinalEdits() {
  const edits = buildFinalEdits();
  const text = JSON.stringify(edits, null, 2);
  document.getElementById("section-final-edits").textContent = text;
  const blob = new Blob([text], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `section-final-edits-${sectionPackage.section_id}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

document.getElementById("copy-original").addEventListener("click", () => copyText("original-text"));
document.getElementById("copy-suggested").addEventListener("click", () => copyText("suggested-text"));
document.getElementById("previous-item").addEventListener("click", () => goTo(-1));
document.getElementById("next-item").addEventListener("click", () => goTo(1));
document.getElementById("submit-section").addEventListener("click", downloadSectionFinalEdits);
loadCurrentItem();
```

- [ ] **Step 5: Update CSS for section layout**

Append to `assets/workbench/workbench.css`:

```css
.section-header {
  margin-bottom: 24px;
}

.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.panel-title h2 {
  margin: 0;
}

#final-text,
#agent-discussion {
  min-height: 140px;
}
```

- [ ] **Step 6: Implement section workbench builder**

Create `scripts/build_section_workbench.py`:

```python
#!/usr/bin/env python3
import html
import json
import sys
from pathlib import Path

from validate_section_polish_package import validate


ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "assets" / "workbench"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def script_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")


def load_asset(name: str) -> str:
    return (ASSET_DIR / name).read_text(encoding="utf-8")


def render(package: dict) -> str:
    rendered = load_asset("section-workbench.html")
    replacements = {
        "__WORKBENCH_CSS__": load_asset("workbench.css"),
        "__SECTION_WORKBENCH_JS__": load_asset("section-workbench.js"),
        "__SECTION_TITLE__": esc(package["section_title"]),
        "__SECTION_PACKAGE_JSON__": script_json(package),
    }
    for token, value in replacements.items():
        rendered = rendered.replace(token, value)
    return rendered


def run(package_path: Path, output_path: Path) -> dict:
    package = json.loads(package_path.read_text(encoding="utf-8"))
    summary = validate(package)
    if not summary["ok"]:
        return summary
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render(package), encoding="utf-8")
    return {
        "ok": True,
        "output": str(output_path),
        "section_id": package["section_id"],
        "item_count": len(package["items"]),
        "errors": [],
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: build_section_workbench.py SECTION_PACKAGE_JSON OUTPUT_HTML", file=sys.stderr)
        return 2
    summary = run(Path(argv[1]), Path(argv[2]))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 7: Run section workbench tests**

Run:

```bash
pytest tests/test_build_section_workbench.py -q
```

Expected: PASS.

- [ ] **Step 8: Run related workbench tests**

Run:

```bash
pytest tests/test_build_workbench.py tests/test_prepare_workbench_review_state.py tests/test_build_section_workbench.py -q
```

Expected: PASS.

- [ ] **Step 9: Commit section workbench generator**

Run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher add scripts/build_section_workbench.py assets/workbench/section-workbench.html assets/workbench/section-workbench.js assets/workbench/workbench.css tests/test_build_section_workbench.py
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher commit -m "feat: add section workbench generator"
```

Expected: commit succeeds.

## Task 4: Manual Validation Output

**Files:**
- Modify: `architecture.md`
- Modify: `references/knowledge.md`

- [ ] **Step 1: Generate manual section workbench**

Run:

```bash
python scripts/build_section_workbench.py tests/fixtures/section-workbench/section-polish-package-introduction.json /data/latex_test/section-workbench-introduction.html
```

Expected: command prints JSON with `"ok": true` and writes `/data/latex_test/section-workbench-introduction.html`.

- [ ] **Step 2: Verify generated HTML contains required controls**

Run:

```bash
rg -n "Previous Paragraph|Next Paragraph|Submit Whole Section|copy-original|copy-suggested|downloadSectionFinalEdits" /data/latex_test/section-workbench-introduction.html
```

Expected: output contains all listed strings.

- [ ] **Step 3: Ensure static server is available**

Run:

```bash
curl -I http://127.0.0.1:3111/section-workbench-introduction.html
```

Expected: `HTTP/1.0 200 OK` if the existing `/data/latex_test` static server is running. If it is not running, start it with:

```bash
python -m http.server 3111 --bind 0.0.0.0
```

from `/data/latex_test`.

- [ ] **Step 4: Update architecture runtime artifact note if needed**

If manual validation reveals a new output filename pattern, update `architecture.md`. Otherwise do not edit docs.

- [ ] **Step 5: Run full tests**

Run:

```bash
pytest -q
```

Expected: all tests pass.

- [ ] **Step 6: Commit docs if changed**

If `architecture.md` or `references/knowledge.md` changed, run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher add architecture.md references/knowledge.md
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher commit -m "docs: document section workbench validation outputs"
```

If no docs changed, skip this commit.

## Task 5: Final Verification And Push

**Files:**
- Read/verify all files changed in Tasks 1-4.

- [ ] **Step 1: Run full test suite**

Run:

```bash
pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Check whitespace**

Run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher diff --check
```

Expected: no output.

- [ ] **Step 3: Check worktree status**

Run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher status --short
```

Expected: no tracked or untracked files except ignored local runtime artifacts.

- [ ] **Step 4: Push commits**

Run:

```bash
git --git-dir=/tmp/latex-paper-polisher.git --work-tree=/data/latex-paper-polisher push
```

Expected: local commits are pushed to `origin/main`.

## Self-Review Notes

- Spec coverage: paper summary schema, section polish package, browser-local previous/next navigation, copy buttons, editable final text defaulting to original text, discussion area, section-final-edits download, and no source writeback are all covered.
- Runtime boundary: generated HTML and section JSON remain under `/data/latex_test`; reusable assets stay under `assets/workbench/`.
- TDD coverage: validator behavior and HTML generation are covered before implementation.
