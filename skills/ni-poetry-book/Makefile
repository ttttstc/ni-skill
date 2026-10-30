PYTHON ?= python3
THEMES ?= song-mist celadon ink-zen cinnabar-seal moon-river bamboo

.PHONY: install test examples article-examples check clean

install:
	$(PYTHON) scripts/install.py

test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v

examples:
	rm -rf dist/poetry
	set -e; for theme in $(THEMES); do \
		$(PYTHON) scripts/render_book.py --input examples/book.json --theme "$$theme" --output "dist/poetry/$$theme"; \
	done

article-examples:
	rm -rf dist/technical-fixture dist/technical-fixture-assets
	$(PYTHON) scripts/render_article.py --input examples/technical-fixture.md --offline --output dist/technical-fixture --theme ink-zen --require "long_value" --require "Prefill"

check: test examples article-examples

clean:
	rm -rf dist
