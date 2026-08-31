#!/usr/bin/env python3
"""Copy a generated Markdown transcript to an archive path without overwriting."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


class ArchiveError(RuntimeError):
    """A user-actionable archive failure."""


def archive_markdown(source: Path, destination: Path) -> Path:
    source = source.expanduser().resolve()
    if not source.is_file():
        raise ArchiveError(f"找不到待归档的 Markdown：{source}")
    if source.suffix.lower() != ".md":
        raise ArchiveError("只允许归档 .md 文件。")

    destination = destination.expanduser()
    if destination.exists() and destination.is_dir():
        target = destination / source.name
    elif destination.suffix.lower() == ".md":
        target = destination
    else:
        target = destination / source.name
    target = target.resolve()

    if target == source:
        raise ArchiveError("归档目标不能与原 Markdown 相同。")
    if target.exists():
        raise ArchiveError(f"归档目标已存在，为避免覆盖已停止：{target}")

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as input_stream, target.open("xb") as output_stream:
            shutil.copyfileobj(input_stream, output_stream)
        shutil.copystat(source, target)
    except OSError as exc:
        target.unlink(missing_ok=True)
        raise ArchiveError(f"归档 Markdown 失败：{target}") from exc
    return target


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="将 Markdown 文字稿安全复制到归档路径。")
    parser.add_argument("source", type=Path, help="待归档的 .md 文件")
    parser.add_argument("destination", type=Path, help="归档目录或目标 .md 路径")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        target = archive_markdown(args.source, args.destination)
    except ArchiveError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    print(f"已归档 Markdown：{target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
