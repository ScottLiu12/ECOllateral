.PHONY: lint test run ingest demo train sensitivity
PYTHON ?= python

lint:
	$(PYTHON) -m ruff check src tests
	$(PYTHON) -m ruff format --check src tests

test:
	$(PYTHON) -m pytest

run:
	$(PYTHON) -m uvicorn src.api.app:app --reload

ingest:
	$(PYTHON) -m src.cli ingest $(ARGS)

demo:
	$(PYTHON) -m src.cli demo

train:
	$(PYTHON) -m src.cli train $(ARGS)

sensitivity:
	$(PYTHON) -m src.cli sensitivity $(ARGS)
