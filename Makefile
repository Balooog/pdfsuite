.PHONY: venv install dev doctor format lint test doclint smoke

venv:
	python3 -m venv .venv
	. .venv/bin/activate; pip install -U pip

install: venv
	. .venv/bin/activate; pip install -e .

dev: install
	. .venv/bin/activate; pip install black isort ruff pytest pytest-cov mdformat

doctor:
	. .venv/bin/activate; python scripts/doctor.py

format:
	. .venv/bin/activate; black . && isort .

lint:
	. .venv/bin/activate; ruff check . || true

test: install
	. .venv/bin/activate; pip install -e .[test]
	. .venv/bin/activate; pytest

doclint:
	. .venv/bin/activate; git ls-files '*.md' | xargs mdformat --wrap no --check

smoke:
	bash scripts/smoke_test.sh
