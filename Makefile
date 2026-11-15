# Owner: Developer A. Every target wraps one command; README lists the plain commands.
ifeq ($(OS),Windows_NT)
PY ?= $(CURDIR)/.venv/Scripts/python
else
PY ?= $(CURDIR)/.venv/bin/python
endif

.PHONY: setup mock status api web test build

setup:
	python -m venv .venv
	$(PY) -m pip install -r backend/requirements.txt
	npm install --prefix frontend

mock:
	cd backend && $(PY) -m app.cli seed-mock

status:
	cd backend && $(PY) -m app.cli status

api:
	cd backend && $(PY) -m uvicorn app.main:app --reload

web:
	npm run dev --prefix frontend

test:
	$(PY) -m pytest -q

build:
	npm run build --prefix frontend
