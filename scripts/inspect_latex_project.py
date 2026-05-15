#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
SECTION_RE = re.compile(r"\\(section|subsection|subsubsection)\{([^}]+)\}")
CAPTION_RE = re.compile(r"\\caption\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", re.DOTALL)
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
CITE_RE = re.compile(r"\\(?:cite|parencite|textcite|citep|citet)\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:ref|autoref|cref|Cref)\{([^}]+)\}")
MATH_RE = re.compile(r"(?<!\\)\$[^$]+(?<!\\)\$")
CJK_OR_FULLWIDTH_RE = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_tex_suffix(name: str) -> str:
    return name if name.endswith(".tex") else f"{name}.tex"


def find_main_file(project: Path) -> Path:
    tex_files = sorted(project.glob("*.tex"))
    for path in tex_files:
        text = read_text(path)
        if "\\begin{document}" in text:
            return path
    if tex_files:
        return tex_files[0]
    raise SystemExit(f"No .tex files found in {project}")


def expand_files(project: Path, main: Path) -> list[Path]:
    seen: set[Path] = set()
    ordered: list[Path] = []

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in seen:
            return
        seen.add(path)
        ordered.append(path)
        text = read_text(path)
        for match in INPUT_RE.finditer(text):
            child = project / strip_tex_suffix(match.group(1))
            if child.exists():
                visit(child)

    visit(main)
    return ordered


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def extract_constructs(text: str) -> dict:
    citations = []
    for match in CITE_RE.finditer(text):
        citations.extend(part.strip() for part in match.group(1).split(",") if part.strip())
    refs = []
    for match in REF_RE.finditer(text):
        refs.extend(part.strip() for part in match.group(1).split(",") if part.strip())
    return {
        "citations": citations,
        "refs": refs,
        "labels": LABEL_RE.findall(text),
        "math_spans": MATH_RE.findall(text),
        "has_cjk_or_fullwidth": bool(CJK_OR_FULLWIDTH_RE.search(text)),
    }


def paragraph_blocks(text: str) -> list[tuple[int, int, str]]:
    blocks = []
    offset = 0
    for raw in re.split(r"\n\s*\n", text):
        start = text.find(raw, offset)
        offset = start + len(raw)
        block = raw.strip()
        if not block:
            continue
        if block.startswith("\\") and not block.startswith("\\caption"):
            continue
        blocks.append((start, start + len(raw), block))
    return blocks


def inspect_file(project: Path, path: Path) -> tuple[list[dict], list[dict]]:
    rel = path.relative_to(project).as_posix()
    text = read_text(path)
    sections = []
    paragraphs = []
    for match in SECTION_RE.finditer(text):
        sections.append({
            "level": match.group(1),
            "title": match.group(2),
            "file": rel,
            "line": line_number(text, match.start()),
        })

    caption_ranges = []
    for match in CAPTION_RE.finditer(text):
        caption_ranges.append((match.start(), match.end()))
        nearby = text[match.end(): match.end() + 300]
        label_match = LABEL_RE.search(nearby)
        constructs = extract_constructs(match.group(1))
        paragraphs.append({
            "id": f"{rel}:caption:{len(paragraphs) + 1}",
            "kind": "caption",
            "file": rel,
            "start_line": line_number(text, match.start()),
            "end_line": line_number(text, match.end()),
            "text": match.group(1).strip(),
            "label": label_match.group(1) if label_match else None,
            **constructs,
        })

    for start, end, block in paragraph_blocks(text):
        if any(start >= cap_start and end <= cap_end for cap_start, cap_end in caption_ranges):
            continue
        if block.startswith("\\begin") or block.startswith("\\end") or block.startswith("\\section"):
            continue
        constructs = extract_constructs(block)
        paragraphs.append({
            "id": f"{rel}:paragraph:{len(paragraphs) + 1}",
            "kind": "paragraph",
            "file": rel,
            "start_line": line_number(text, start),
            "end_line": line_number(text, end),
            "text": block,
            "label": None,
            **constructs,
        })
    paragraphs.sort(key=lambda item: (item["file"], item["start_line"]))
    return sections, paragraphs


def inspect(project: Path) -> dict:
    project = project.resolve()
    main = find_main_file(project)
    files = expand_files(project, main)
    all_sections = []
    all_paragraphs = []
    for path in files:
        sections, paragraphs = inspect_file(project, path)
        all_sections.extend(sections)
        all_paragraphs.extend(paragraphs)
    return {
        "project": str(project),
        "main_file": main.relative_to(project).as_posix(),
        "files": [path.relative_to(project).as_posix() for path in files],
        "sections": all_sections,
        "paragraphs": all_paragraphs,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: inspect_latex_project.py PROJECT_DIR", file=sys.stderr)
        return 2
    data = inspect(Path(argv[1]))
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
