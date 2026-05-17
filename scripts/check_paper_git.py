#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


def git_command(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(path), *args],
        text=True,
        capture_output=True,
    )


def parse_status_line(line: str) -> dict:
    status = line[:2].strip() or line[:2]
    path = line[3:]
    return {"status": status, "path": path}


def parse_dirty_files(status_output: str) -> list[dict]:
    return [
        parse_status_line(line)
        for line in status_output.splitlines()
        if line.strip()
    ]


def inspect_git(path: Path) -> tuple[int, dict]:
    if not path.exists() or not path.is_dir():
        return 1, {
            "ok": False,
            "is_git_repo": False,
            "repo_root": "",
            "branch": "",
            "dirty_files": [],
            "errors": [f"path is not a directory: {path}"],
        }

    root_result = git_command(path, "rev-parse", "--show-toplevel")
    if root_result.returncode != 0:
        return 1, {
            "ok": False,
            "is_git_repo": False,
            "repo_root": "",
            "branch": "",
            "dirty_files": [],
            "errors": ["not a git repository"],
        }

    branch_result = git_command(path, "branch", "--show-current")
    status_result = git_command(path, "status", "--short")
    errors = []
    if branch_result.returncode != 0:
        errors.append(branch_result.stderr.strip() or "failed to read current branch")
    if status_result.returncode != 0:
        errors.append(status_result.stderr.strip() or "failed to read git status")

    data = {
        "ok": not errors,
        "is_git_repo": True,
        "repo_root": root_result.stdout.strip(),
        "branch": branch_result.stdout.strip() if branch_result.returncode == 0 else "",
        "dirty_files": parse_dirty_files(status_result.stdout) if status_result.returncode == 0 else [],
        "errors": errors,
    }
    return (0 if data["ok"] else 1), data


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_paper_git.py PAPER_ROOT", file=sys.stderr)
        return 2
    exit_code, data = inspect_git(Path(argv[1]))
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
