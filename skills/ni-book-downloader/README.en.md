# ni-book-downloader

[中文](./README.md) | English

> Download ebooks by title, strictly separating text formats (epub/mobi/azw3/fb2/txt) from layout formats (PDF), and confirm the preferred format before searching.

`ni-book-downloader` aggregates five channels (GitHub ebook index / ctfile, LibGen, Z-Library, Anna's Archive, and a web-search fallback) with a no-quota-first fallback chain. When only a PDF is available but you need text, it extracts the PDF text layer as a fallback. Full rules, commands, and acceptance criteria live in [SKILL.md](./SKILL.md).

## Quick start

```bash
python scripts/book.py setup --launch-chrome   # first run: diagnose and open the login window (Z-Library only)
python scripts/book.py search "TITLE" --format text   # list candidates without downloading
python scripts/book.py auto "TITLE" --format text -o /path/to/books
python scripts/book.py extract-pdf book.pdf   # extract text layer from a digital-born PDF
```

## Channels and fallback order

| Order | Channel | Account and quota | Notes |
|-------|---------|-------------------|-------|
| 1 | GitHub ebook index / ctfile | No account, no quota | Main source for Chinese text-format books, ~24k entries indexed |
| 2 | LibGen | No account, no quota | Main source for English books, resumable downloads |
| 3 | Z-Library | Login required, ~10 books/day for free accounts | Chinese-book supplement; quota resets the next day |
| 4 | Anna's Archive | No account (slow) | Aggregated-source supplement |
| 5 | Web search fallback | Netdisk links need your own account | Multi-engine search extracting all netdisk types and direct links |

## Format semantics

| Flag | Behavior |
|------|----------|
| `--format text` | Text formats only (epub/mobi/azw3/fb2/txt) |
| `--format pdf` | PDF only |
| Unspecified (default) | All formats allowed, auto-ranked: epub > txt > pdf > mobi/azw3 |

## Evaluation and self-check

```bash
python tests/smoke_test.py
```

`evals/` holds the skill-up evaluation config (8 cases, 8/8 passing). The offline smoke suite needs no network and verifies the scripts and matching logic.

## Dependencies and boundaries

- Python 3.10+, dependencies in `requirements.txt` (requests / websocket-client / pymupdf).
- Z-Library and the web-search fallback run through a companion Chrome instance (CDP debug port). On first use, `setup --launch-chrome` opens the window for you to log in; the skill never touches your password.
- The proxy defaults to `http://127.0.0.1:7890` and can be overridden by environment variables; engine order, browser, and cache locations are documented in SKILL.md.
- If the agent engine's safety policy refuses download requests, the skill delivers the candidate list and stops; it never bypasses the policy.
