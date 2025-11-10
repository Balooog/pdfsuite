.PHONY: venv install dev doctor format lint test smoke

venv:
	python3 -m venv .venv
	. .venv/bin/activate; pip install -U pip

install: venv
	. .venv/bin/activate; pip install -e .

dev: install
	. .venv/bin/activate; pip install black isort ruff

doctor:
	. .venv/bin/activate; python scripts/doctor.py

format:
	. .venv/bin/activate; black . && isort .

lint:
	. .venv/bin/activate; ruff check . || true

smoke:
	bash scripts/smoke_test.sh
