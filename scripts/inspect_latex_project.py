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


def make_anchor(file: str, line: int, kind: str, title: str | None = None) -> dict:
    anchor = {"file": file, "line": line, "kind": kind}
    if title is not None:
        anchor["title"] = title
    return anchor


def extract_sections(file: str, text: str) -> list[dict]:
    sections = []
    for match in SECTION_RE.finditer(text):
        line = line_number(text, match.start())
        sections.append({
            "level": match.group(1),
            "title": match.group(2),
            "file": file,
            "line": line,
            "anchor": make_anchor(file, line, "section", match.group(2)),
        })
    return sections


def extract_captions(file: str, text: str) -> list[dict]:
    captions = []
    for match in CAPTION_RE.finditer(text):
        line = line_number(text, match.start())
        nearby = text[match.end(): match.end() + 300]
        label_match = LABEL_RE.search(nearby)
        captions.append({
            "file": file,
            "line": line,
            "text": match.group(1).strip(),
            "label": label_match.group(1) if label_match else None,
            "anchor": make_anchor(file, line, "caption"),
        })
    return captions


def extract_keyed_constructs(file: str, text: str, pattern: re.Pattern, kind: str) -> list[dict]:
    return [
        {"file": file, "line": line_number(text, match.start()), "kind": kind, "key": match.group(1)}
        for match in pattern.finditer(text)
    ]


def extract_multi_keyed_constructs(file: str, text: str, pattern: re.Pattern, kind: str) -> list[dict]:
    items = []
    for match in pattern.finditer(text):
        for key in match.group(1).split(","):
            key = key.strip()
            if key:
                items.append({"file": file, "line": line_number(text, match.start()), "kind": kind, "key": key})
    return items


def detect_protected_regions(file: str, text: str) -> list[dict]:
    regions = []
    begin_doc = text.find("\\begin{document}")
    if begin_doc > 0:
        regions.append({
            "file": file,
            "kind": "preamble",
            "start_line": 1,
            "end_line": line_number(text, begin_doc),
            "reason": "LaTeX preamble is not a polishing task.",
        })
    for env in ("table", "tabular", "rawbox", "algorithm", "align", "equation"):
        pattern = re.compile(rf"\\begin\{{{env}\}}.*?\\end\{{{env}\}}", re.DOTALL)
        for match in pattern.finditer(text):
            regions.append({
                "file": file,
                "kind": f"environment:{env}",
                "start_line": line_number(text, match.start()),
                "end_line": line_number(text, match.end()),
                "reason": f"{env} environment should not be treated as ordinary prose.",
            })
    return regions


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


def build_project_map(project: Path) -> dict:
    project = project.resolve()
    main = find_main_file(project)
    files = expand_files(project, main)
    sections: list[dict] = []
    captions: list[dict] = []
    labels: list[dict] = []
    refs: list[dict] = []
    citations: list[dict] = []
    protected_regions: list[dict] = []

    for path in files:
        rel = path.relative_to(project).as_posix()
        text = read_text(path)
        protected_regions.extend(detect_protected_regions(rel, text))
        sections.extend(extract_sections(rel, text))
        captions.extend(extract_captions(rel, text))
        labels.extend(extract_keyed_constructs(rel, text, LABEL_RE, "label"))
        refs.extend(extract_multi_keyed_constructs(rel, text, REF_RE, "ref"))
        citations.extend(extract_multi_keyed_constructs(rel, text, CITE_RE, "citation"))

    return {
        "schema_version": 2,
        "mode": "project_map",
        "project_root": str(project),
        "main_file": main.relative_to(project).as_posix(),
        "files": [path.relative_to(project).as_posix() for path in files],
        "sections": sections,
        "captions": captions,
        "labels": labels,
        "refs": refs,
        "citations": citations,
        "protected_regions": protected_regions,
    }


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "--map":
        print(json.dumps(build_project_map(Path(argv[2])), ensure_ascii=False, indent=2))
        return 0
    if len(argv) == 2:
        data = inspect(Path(argv[1]))
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print("usage: inspect_latex_project.py [--map] PROJECT_DIR", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
