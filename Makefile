# Owner: Lead. Every target wraps one command; see README for the plain commands.
ifeq ($(OS),Windows_NT)
PY ?= .venv/Scripts/python
else
PY ?= .venv/bin/python
endif
LLM ?=
ACTIVATE ?=

.PHONY: setup mock spike fetch giovanni process analyse explain build test web-dev web-build

setup:
	python -m venv .venv
	$(PY) -m pip install -r requirements.txt
	npm ci --prefix web

mock:
	$(PY) -m pipeline.make_mock

spike:
	$(PY) -m pipeline.inspect_granule

fetch:
	$(PY) -m pipeline.fetch_imerg

giovanni:
	$(PY) -m pipeline.import_giovanni $(FILE) $(if $(ACTIVATE),--activate,)

process:
	$(PY) -m pipeline.aggregate

analyse:
	$(PY) -m pipeline.analyse

explain:
	$(PY) -m pipeline.explain $(if $(LLM),--llm,)

build:
	$(PY) -m pipeline.build $(if $(LLM),--llm,)

test:
	$(PY) -m pytest -q

web-dev:
	npm run dev --prefix web

web-build:
	npm run build --prefix web
