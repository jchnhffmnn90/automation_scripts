.PHONY: help install install-dev test test-cov lint format typecheck check clean pre-commit-install

PYTHON ?= python3

help:
	@echo "Automation Scripts - DevOps & Development Commands"
	@echo "=================================================="
	@echo "make install            - Install package in editable mode"
	@echo "make install-dev        - Install package with development dependencies"
	@echo "make test               - Run test suite with unittest / pytest"
	@echo "make test-cov           - Run tests with coverage report"
	@echo "make lint               - Run Ruff linter"
	@echo "make format             - Format code with Ruff"
	@echo "make format-check       - Check code formatting with Ruff"
	@echo "make typecheck          - Run Mypy static type checker"
	@echo "make check              - Run full validation pipeline (lint, format-check, typecheck, test)"
	@echo "make pre-commit-install - Install and configure git pre-commit hooks"
	@echo "make clean              - Remove temporary and cached build files"

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m unittest test_organizer.py -v

test-cov:
	pytest --cov=organizer --cov-report=term-missing --cov-report=html

lint:
	ruff check .

format:
	ruff format .

format-check:
	ruff format --check .

typecheck:
	mypy organizer.py test_organizer.py

check:
	@echo "==> Running Lint Checks..."
	ruff check .
	@echo "==> Checking Formatting..."
	ruff format --check .
	@echo "==> Running Type Checks..."
	mypy organizer.py test_organizer.py
	@echo "==> Running Test Suite..."
	$(PYTHON) -m unittest test_organizer.py -v
	@echo "==> All validation checks passed!"

pre-commit-install:
	pre-commit install

clean:
	rm -rf build/ dist/ *.egg-info/ .eggs/
	rm -rf .pytest_cache/ .ruff_cache/ .mypy_cache/ htmlcov/ .coverage coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
