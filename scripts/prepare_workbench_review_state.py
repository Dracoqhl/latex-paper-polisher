#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def next_commands(decision_path: Path, candidate_path: Path) -> list[str]:
    return [
        f"python scripts/prepare_writeback_candidate.py {decision_path} {candidate_path}",
        "Future writeback must still be explicitly approved before any source file is modified.",
    ]


def merge_state(payload: dict, decision: dict, candidate: dict, decision_path: Path, candidate_path: Path) -> dict:
    enriched = dict(payload)
    enriched["review_status"] = {
        "decision": decision["decision"],
        "ready_for_writeback": decision["ready_for_writeback"],
        "review_notes": decision.get("review_notes", ""),
    }
    enriched["writeback_candidate"] = {
        "available": candidate.get("mode") == "writeback_candidate",
        "validation_required": candidate.get("validation_required", True),
        "source_write_permitted": candidate.get("source_write_permitted", False),
        "line_range": candidate.get("line_range"),
    }
    enriched["next_commands"] = next_commands(decision_path, candidate_path)
    return enriched


def run(payload_path: Path, decision_path: Path, candidate_path: Path, output_path: Path) -> dict:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    enriched = merge_state(payload, decision, candidate, decision_path, candidate_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "output": str(output_path),
    }


def main(argv: list[str]) -> int:
    if len(argv) != 5:
        print(
            "usage: prepare_workbench_review_state.py WORKBENCH_PAYLOAD_JSON REVIEW_DECISION_JSON WRITEBACK_CANDIDATE_JSON OUTPUT_JSON",
            file=sys.stderr,
        )
        return 2
    summary = run(Path(argv[1]), Path(argv[2]), Path(argv[3]), Path(argv[4]))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
