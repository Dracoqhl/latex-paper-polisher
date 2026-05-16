#!/usr/bin/env python3
import html
import json
import sys
from pathlib import Path

from validate_paper_summary import validate


STYLE = """
body { font-family: system-ui, sans-serif; margin: 32px; line-height: 1.55; color: #1f2933; background: #f8fafc; }
main { max-width: 1120px; margin: 0 auto; }
h1 { font-size: 30px; margin-bottom: 4px; }
h2 { margin-top: 0; }
.meta { color: #52606d; margin-bottom: 24px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
section { border: 1px solid #d9e2ec; border-radius: 8px; padding: 16px; background: #fff; }
.full { grid-column: 1 / -1; }
ul, ol { padding-left: 22px; }
code { background: #f0f4f8; padding: 1px 4px; border-radius: 4px; }
table { width: 100%; border-collapse: collapse; }
th, td { border-bottom: 1px solid #d9e2ec; padding: 8px; text-align: left; vertical-align: top; }
th { background: #f0f4f8; }
""".strip()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def list_items(values: list) -> str:
    if not values:
        return "<li>None.</li>"
    return "".join(f"<li>{esc(value)}</li>" for value in values)


def section_rows(section_map: list) -> str:
    if not section_map:
        return '<tr><td colspan="4">No sections.</td></tr>'
    rows = []
    for section in section_map:
        rows.append(
            "<tr>"
            f"<td><code>{esc(section.get('section_id', ''))}</code></td>"
            f"<td>{esc(section.get('title', ''))}</td>"
            f"<td><code>{esc(section.get('source_file', ''))}</code></td>"
            f"<td>{esc(section.get('role', ''))}</td>"
            "</tr>"
        )
    return "".join(rows)


def render(summary: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Paper Overview</title>
  <style>{STYLE}</style>
</head>
<body>
<main>
  <header>
    <h1>Paper Overview</h1>
    <div class="meta"><code>{esc(summary.get('main_file', ''))}</code> · <code>{esc(summary.get('project_root', ''))}</code></div>
  </header>
  <div class="grid">
    <section class="full">
      <h2>Thesis</h2>
      <p>{esc(summary.get('thesis', ''))}</p>
    </section>
    <section>
      <h2>Contributions</h2>
      <ol>{list_items(summary.get('contributions', []))}</ol>
    </section>
    <section>
      <h2>Terminology</h2>
      <ul>{list_items(summary.get('terminology', []))}</ul>
    </section>
    <section>
      <h2>Macro Risks</h2>
      <ul>{list_items(summary.get('macro_risks', []))}</ul>
    </section>
    <section>
      <h2>Structural Suggestions</h2>
      <ul>{list_items(summary.get('structural_suggestions', []))}</ul>
    </section>
    <section class="full">
      <h2>Section Map</h2>
      <table>
        <thead><tr><th>ID</th><th>Title</th><th>File</th><th>Role</th></tr></thead>
        <tbody>{section_rows(summary.get('section_map', []))}</tbody>
      </table>
    </section>
    <section class="full">
      <h2>Polishing Guidance</h2>
      <ul>{list_items(summary.get('polishing_guidance', []))}</ul>
    </section>
  </div>
</main>
</body>
</html>
"""


def run(summary_path: Path, output_path: Path) -> dict:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    validation = validate(summary)
    if not validation["ok"]:
        return {"ok": False, "output": None, "section_count": validation.get("section_count", 0), "errors": validation["errors"]}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render(summary), encoding="utf-8")
    return {"ok": True, "output": str(output_path), "section_count": len(summary.get("section_map", [])), "errors": []}


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: build_paper_overview.py PAPER_SUMMARY_JSON OUTPUT_HTML", file=sys.stderr)
        return 2
    status = run(Path(argv[1]), Path(argv[2]))
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0 if status["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
