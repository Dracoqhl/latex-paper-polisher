#!/usr/bin/env python3
import json
import sys
from pathlib import Path


VALID_DECISIONS = {"accept", "revise", "reject"}


def parse_final_text(args: list[str]) -> str | None:
    if not args:
        return None
    if len(args) == 2 and args[0] == "--final-text":
        return args[1]
    raise ValueError("usage: record_review_decision.py WORKBENCH_PAYLOAD_JSON accept|revise|reject REVIEW_NOTES OUTPUT_JSON [--final-text TEXT]")


def final_text_for_decision(payload: dict, decision: str, explicit_final_text: str | None) -> str:
    if decision == "accept":
        return explicit_final_text if explicit_final_text is not None else payload["suggested_text"]
    if decision == "revise":
        if explicit_final_text is None:
            raise ValueError("revise requires --final-text")
        return explicit_final_text
    return ""


def build_decision(payload: dict, decision: str, review_notes: str, explicit_final_text: str | None) -> dict:
    if decision not in VALID_DECISIONS:
        raise ValueError(f"decision must be one of: {', '.join(sorted(VALID_DECISIONS))}")
    final_text = final_text_for_decision(payload, decision, explicit_final_text)
    return {
        "schema_version": 1,
        "mode": "main_agent_review_decision",
        "paragraph_id": payload["paragraph_id"],
        "source_file": payload["source_file"],
        "section": payload["section"],
        "decision": decision,
        "review_notes": review_notes,
        "original_text": payload["original_text"],
        "suggested_text": payload["suggested_text"],
        "final_text": final_text,
        "ready_for_writeback": decision in {"accept", "revise"},
        "metadata": {
            "source_payload_metadata": payload.get("metadata", {}),
        },
    }


def run(payload_path: Path, decision: str, review_notes: str, output_path: Path, final_text: str | None) -> dict:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    record = build_decision(payload, decision, review_notes, final_text)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "output": str(output_path),
        "decision": decision,
        "ready_for_writeback": record["ready_for_writeback"],
    }


def main(argv: list[str]) -> int:
    if len(argv) < 5:
        print("usage: record_review_decision.py WORKBENCH_PAYLOAD_JSON accept|revise|reject REVIEW_NOTES OUTPUT_JSON [--final-text TEXT]", file=sys.stderr)
        return 2
    try:
        final_text = parse_final_text(argv[5:])
        summary = run(Path(argv[1]), argv[2], argv[3], Path(argv[4]), final_text)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
