# Log Schema

Local logs are JSON Lines files stored under `.latex-paper-polisher/logs/`.

The log directory must not be pushed to GitHub.

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
