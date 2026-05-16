#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def validate_decision(decision: dict) -> None:
    if decision.get("mode") != "main_agent_review_decision":
        raise ValueError("input is not a main-agent review decision")
    if not decision.get("ready_for_writeback"):
        raise ValueError("decision is not ready for writeback")
    if decision.get("decision") not in {"accept", "revise"}:
        raise ValueError("decision must be accept or revise")
    if not decision.get("original_text"):
        raise ValueError("original_text must not be empty")
    if not decision.get("final_text"):
        raise ValueError("final_text must not be empty")


def build_candidate(decision: dict) -> dict:
    metadata = decision.get("metadata", {}).get("source_payload_metadata", {})
    return {
        "schema_version": 1,
        "mode": "writeback_candidate",
        "paragraph_id": decision["paragraph_id"],
        "source_file": decision["source_file"],
        "section": decision["section"],
        "decision": decision["decision"],
        "original_text": decision["original_text"],
        "final_text": decision["final_text"],
        "line_range": metadata.get("line_range"),
        "validation_required": True,
        "source_write_permitted": False,
        "metadata": {
            "review_notes": decision.get("review_notes", ""),
            "task_type": metadata.get("task_type"),
            "assigned_role": metadata.get("assigned_role"),
        },
    }


def run(decision_path: Path, output_path: Path) -> dict:
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    validate_decision(decision)
    candidate = build_candidate(decision)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "output": str(output_path),
        "validation_required": True,
        "source_write_permitted": False,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: prepare_writeback_candidate.py REVIEW_DECISION_JSON OUTPUT_JSON", file=sys.stderr)
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
