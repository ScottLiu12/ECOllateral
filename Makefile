.PHONY: lint test run ingest demo train sensitivity notebook
PYTHON ?= python

lint:
	$(PYTHON) -m ruff check src tests scripts
	$(PYTHON) -m ruff format --check src tests scripts

test:
	$(PYTHON) -m pytest

run:
	$(PYTHON) -m uvicorn src.api.app:app --reload

ingest demo train sensitivity:
	$(PYTHON) -m src.cli $@ $(ARGS)

notebook:
	$(PYTHON) scripts/run_notebook.py
