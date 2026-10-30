#!/usr/bin/env python3
import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_deck.py <index.html>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1]).expanduser().resolve()
    if not path.is_file():
        print(f"error: {path} not found", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    slides = len(re.findall(r'<section\s+class="[^"]*\bslide\b', text))
    notes = len(re.findall(r'<(?:aside|div)\s+class="notes"', text))
    missing = []

    for required in ("base.css", "runtime.js", "neat-annotations.css"):
        if required not in text:
            missing.append(required)

    if slides < 1:
        print("error: no slides found")
        return 1
    if notes != slides:
        print(f"error: {slides} slides but {notes} notes")
        return 1
    if missing:
        print("error: missing resources: " + ", ".join(missing))
        return 1

    print(f"ok: {slides} slides, {notes} notes, required resources present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
