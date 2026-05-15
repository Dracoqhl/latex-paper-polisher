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
