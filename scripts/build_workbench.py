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
