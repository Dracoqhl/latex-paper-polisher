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
