#!/usr/bin/env python3
import html
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "assets" / "workbench"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def list_items(items: list[str]) -> str:
    if not items:
        return "<li>None.</li>"
    return "\n".join(f"<li>{esc(item)}</li>" for item in items)


def optional_review_status(payload: dict) -> str:
    status = payload.get("review_status")
    candidate = payload.get("writeback_candidate")
    commands = payload.get("next_commands", [])
    if not status and not candidate and not commands:
        return ""

    status_items = []
    if status:
        status_items.extend([
            f"Decision: {status.get('decision', '')}",
            f"Ready for writeback: {str(status.get('ready_for_writeback', False)).lower()}",
            f"Review notes: {status.get('review_notes', '')}",
        ])
    if candidate:
        status_items.extend([
            f"Candidate available: {str(candidate.get('available', False)).lower()}",
            f"Validation required: {str(candidate.get('validation_required', True)).lower()}",
            f"Source write permitted: {str(candidate.get('source_write_permitted', False)).lower()}",
        ])

    return f"""
    <section class="full">
      <h2>Review Status</h2>
      <ul>{list_items(status_items)}</ul>
    </section>
    <section class="full">
      <h2>Next Commands</h2>
      <ul>{list_items(commands)}</ul>
    </section>"""


def script_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")


def load_asset(name: str) -> str:
    return (ASSET_DIR / name).read_text(encoding="utf-8")


def render(payload: dict) -> str:
    replacements = {
        "__WORKBENCH_CSS__": load_asset("workbench.css"),
        "__WORKBENCH_JS__": load_asset("workbench.js"),
        "__PARAGRAPH_ID__": esc(payload.get("paragraph_id", "")),
        "__SOURCE_FILE__": esc(payload.get("source_file", "")),
        "__SECTION_NAME__": esc(payload.get("section", "")),
        "__ORIGINAL_TEXT__": esc(payload.get("original_text", "")),
        "__SUGGESTED_TEXT__": esc(payload.get("suggested_text", "")),
        "__RATIONALE_ITEMS__": list_items(payload.get("rationale", [])),
        "__WARNING_ITEMS__": list_items(payload.get("warnings", [])),
        "__OPTIONAL_REVIEW_STATUS__": optional_review_status(payload),
        "__PAYLOAD_JSON__": script_json(payload),
    }
    rendered = load_asset("workbench.html")
    for token, value in replacements.items():
        rendered = rendered.replace(token, value)
    return rendered


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: build_workbench.py PAYLOAD_JSON OUTPUT_HTML", file=sys.stderr)
        return 2
    payload = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    Path(argv[2]).write_text(render(payload), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
