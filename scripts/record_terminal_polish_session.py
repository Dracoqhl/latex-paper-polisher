#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path


REQUIRED_KEYS = {
    "timestamp",
    "paper_root",
    "target_section",
    "semantic_unit",
    "source_files_touched",
    "original_excerpt",
    "final_excerpt",
    "user_confirmation",
    "validation",
    "paper_commit_hash",
    "knowledge_updates",
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_record(session: dict) -> dict:
    missing = sorted(REQUIRED_KEYS - set(session))
    if missing:
        raise ValueError(f"missing required terminal session keys: {', '.join(missing)}")
    return {
        "schema_version": 1,
        "mode": "terminal_polish_session",
        "timestamp": session["timestamp"],
        "paper_root": session["paper_root"],
        "target_section": session["target_section"],
        "semantic_unit": session["semantic_unit"],
        "source_files_touched": session["source_files_touched"],
        "original_excerpt_hash": sha256_text(session["original_excerpt"]),
        "final_excerpt_hash": sha256_text(session["final_excerpt"]),
        "user_confirmation": session["user_confirmation"],
        "validation": session["validation"],
        "paper_commit_hash": session["paper_commit_hash"],
        "knowledge_updates": session["knowledge_updates"],
    }


def run(session_path: Path, log_path: Path) -> dict:
    session = json.loads(session_path.read_text(encoding="utf-8"))
    record = build_record(session)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return {
        "ok": True,
        "output": str(log_path),
        "mode": "terminal_polish_session",
        "paper_commit_hash": record["paper_commit_hash"],
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: record_terminal_polish_session.py SESSION_JSON LOG_JSONL", file=sys.stderr)
        return 2
    try:
        summary = run(Path(argv[1]), Path(argv[2]))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
