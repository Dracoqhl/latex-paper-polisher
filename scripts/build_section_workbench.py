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
