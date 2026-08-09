#!/usr/bin/env python3
"""Audit a Chinese-default and English GitHub README pair."""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
MARKDOWN_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+[^)]*)?\)")
MARKDOWN_BADGE = re.compile(
    r"\[!\[([^\]]*)\]\(([^)\s]+)(?:\s+[^)]*)?\)\]"
    r"\(([^)\s]+)(?:\s+[^)]*)?\)"
)
HTML_IMAGE = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"'][^>]*>", re.I)
HTML_ALT = re.compile(r"\balt=[\"']([^\"']*)[\"']", re.I)
FENCED_CODE = re.compile(r"^```[^\n]*\n(.*?)^```\s*$", re.M | re.S)
HEADING = re.compile(r"^(#{1,6})\s+\S", re.M)
REMOTE_PREFIXES = ("http://", "https://", "mailto:", "data:", "#")
LANGUAGE_TARGETS = {"./README.md", "README.md", "./README.en.md", "README.en.md"}
UNSAFE_SVG_TAGS = {"script", "foreignObject"}


def repository_root(argument: str) -> Path:
    path = Path(argument).expanduser().resolve()
    if path.is_dir():
        return path
    if path.is_file() and path.name in {"README.md", "README.en.md"}:
        return path.parent
    raise ValueError(f"expected a repository directory, README.md, or README.en.md: {path}")


def local_target(target: str, base: Path) -> Path | None:
    if target.startswith(REMOTE_PREFIXES):
        return None
    clean = target.split("#", 1)[0].split("?", 1)[0]
    return (base / clean).resolve() if clean else None


def audit_svg(path: Path) -> list[str]:
    issues: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return [f"invalid SVG XML: {exc}"]

    if "viewBox" not in root.attrib:
        issues.append("missing viewBox")

    title_found = False
    for node in root.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        if tag == "title" and (node.text or "").strip():
            title_found = True
        if tag in UNSAFE_SVG_TAGS:
            issues.append(f"contains unsupported <{tag}>")
    if not title_found:
        issues.append("missing non-empty <title>")
    return issues


def markdown_targets(text: str) -> Counter[str]:
    return Counter(
        target
        for target in MARKDOWN_LINK.findall(text)
        if target not in LANGUAGE_TARGETS
    )


def image_targets(text: str) -> Counter[str]:
    targets = [target for _, target in MARKDOWN_IMAGE.findall(text)]
    targets.extend(HTML_IMAGE.findall(text))
    return Counter(targets)


def badge_targets(text: str) -> Counter[tuple[str, str]]:
    return Counter((source, target) for _, source, target in MARKDOWN_BADGE.findall(text))


def compare_pair(chinese: str, english: str) -> list[str]:
    issues: list[str] = []
    if "[English](./README.en.md)" not in chinese:
        issues.append("README.md missing link: [English](./README.en.md)")
    if "[中文](./README.md)" not in english:
        issues.append("README.en.md missing link: [中文](./README.md)")

    chinese_headings = [len(mark) for mark in HEADING.findall(chinese)]
    english_headings = [len(mark) for mark in HEADING.findall(english)]
    if chinese_headings != english_headings:
        issues.append("heading-level sequence differs between README.md and README.en.md")

    if FENCED_CODE.findall(chinese) != FENCED_CODE.findall(english):
        issues.append("fenced code blocks differ between README.md and README.en.md")

    if markdown_targets(chinese) != markdown_targets(english):
        issues.append("Markdown link targets differ between README.md and README.en.md")

    if badge_targets(chinese) != badge_targets(english):
        issues.append("badge sources or targets differ between README.md and README.en.md")

    if image_targets(chinese) != image_targets(english):
        issues.append("image targets differ between README.md and README.en.md")
    return issues


def audit_document(path: Path, text: str) -> tuple[list[str], int]:
    issues: list[str] = []
    targets: list[str] = []

    for alt, src in MARKDOWN_IMAGE.findall(text):
        targets.append(src)
        if not alt.strip():
            issues.append(f"{path.name}: Markdown image missing useful alt text: {src}")

    html_tags = re.findall(r"<img\b[^>]*>", text, flags=re.I)
    targets.extend(HTML_IMAGE.findall(text))
    for tag in html_tags:
        match = HTML_ALT.search(tag)
        if not match or not match.group(1).strip():
            issues.append(f"{path.name}: HTML image missing useful alt text: {tag[:100]}")

    checked = 0
    for src in dict.fromkeys(targets):
        target = local_target(src, path.parent)
        if target is None:
            continue
        checked += 1
        if not target.is_file():
            issues.append(f"{path.name}: missing image: {src}")
            continue
        if target.suffix.lower() == ".svg":
            for issue in audit_svg(target):
                issues.append(f"{path.name}: {src}: {issue}")
    return issues, checked


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: audit_readme.py /path/to/repository", file=sys.stderr)
        return 2

    try:
        root = repository_root(sys.argv[1])
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    chinese_path = root / "README.md"
    english_path = root / "README.en.md"
    missing = [str(path) for path in (chinese_path, english_path) if not path.is_file()]
    if missing:
        print("Issues:")
        for path in missing:
            print(f"- missing required README: {path}")
        return 1

    chinese = chinese_path.read_text(encoding="utf-8")
    english = english_path.read_text(encoding="utf-8")
    issues = compare_pair(chinese, english)

    checked = 0
    for path, text in ((chinese_path, chinese), (english_path, english)):
        document_issues, document_checked = audit_document(path, text)
        issues.extend(document_issues)
        checked += document_checked

    print(f"Repository: {root}")
    print("README pair: README.md (Chinese) + README.en.md (English)")
    print(f"Local images checked: {checked}")
    if issues:
        print("Issues:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("OK: bilingual links, structural parity, image references, and SVG basics passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
