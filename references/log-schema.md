# Log Schema

Local logs are JSON Lines files stored under `.latex-paper-polisher/logs/`.

The log directory must not be committed or pushed. For Terminal-first paper editing, prefer a paper-local ignored log directory so the log can refer to the paper project's own git commit.

Each entry should contain:

```json
{
  "timestamp": "2026-05-14T00:00:00Z",
  "project_path": "/path/to/paper",
  "source_file": "sections/introduction.tex",
  "section": "Introduction",
  "paragraph_id": "sections/introduction.tex:paragraph:1",
  "original_text": "Original paragraph.",
  "suggested_text": "Suggested paragraph.",
  "user_feedback": "User confirmation or requested change.",
  "final_writeback_text": "Final paragraph.",
  "diff_summary": "One paragraph changed.",
  "validation_result": {"ok": true, "warnings": []},
  "commit_hash": "abc1234",
  "knowledge_updates": []
}
```

## Terminal Polishing Session Log

`scripts/record_terminal_polish_session.py` appends compact session records after a user-confirmed source edit has been validated and committed in the paper repository.

Input session JSON contains the original and final excerpts so the helper can compute hashes. The JSONL log stores hashes rather than full text:

```json
{
  "schema_version": 1,
  "mode": "terminal_polish_session",
  "timestamp": "2026-05-17T10:00:00Z",
  "paper_root": "/path/to/paper",
  "target_section": "Abstract",
  "semantic_unit": "opening motivation sentence",
  "source_files_touched": ["main.tex"],
  "original_excerpt_hash": "sha256...",
  "final_excerpt_hash": "sha256...",
  "user_confirmation": "Use the revised sentence.",
  "validation": {
    "commands": ["python scripts/validate_writeback.py before.tex after.tex"],
    "summary": "LaTeX constructs preserved.",
    "ok": true
  },
  "paper_commit_hash": "abc1234",
  "knowledge_updates": []
}
```
