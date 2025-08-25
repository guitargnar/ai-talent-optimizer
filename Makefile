# Makefile for Career Automation System

.PHONY: help install test clean lint format coverage security docs run

help:
	@echo "Career Automation System - Development Commands"
	@echo "================================================"
	@echo "make install    - Install all dependencies"
	@echo "make test       - Run all tests"
	@echo "make test-unit  - Run unit tests only"
	@echo "make test-int   - Run integration tests only"
	@echo "make coverage   - Run tests with coverage report"
	@echo "make lint       - Run linting checks"
	@echo "make format     - Format code automatically"
	@echo "make security   - Run security checks"
	@echo "make clean      - Clean up temporary files"
	@echo "make docs       - Build documentation"
	@echo "make run        - Run the automation system"
	@echo "make git-init   - Initialize git repository"
	@echo "make pre-commit - Install pre-commit hooks"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	@echo "✅ Dependencies installed"

test:
	pytest -v --tb=short

test-unit:
	pytest -v -m unit --tb=short

test-int:
	pytest -v -m integration --tb=short

test-email:
	pytest -v -m email --tb=short

coverage:
	pytest --cov=. --cov-report=html --cov-report=term-missing --cov-fail-under=70
	@echo "📊 Coverage report generated in htmlcov/index.html"

lint:
	@echo "🔍 Running flake8..."
	flake8 . --max-line-length=100 --extend-ignore=E203,W503
	@echo "🔍 Running mypy..."
	mypy . --ignore-missing-imports
	@echo "🔍 Running pylint..."
	pylint *.py --disable=C0114,C0115,C0116
	@echo "✅ Linting complete"

format:
	@echo "🎨 Formatting with black..."
	black . --line-length=100
	@echo "🎨 Sorting imports with isort..."
	isort . --profile black --line-length 100
	@echo "✅ Formatting complete"

security:
	@echo "🔒 Running security checks..."
	bandit -r . -f json -o security-report.json
	safety check --json
	@echo "✅ Security check complete (see security-report.json)"

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage*" -delete
	rm -rf build dist *.egg-info
	rm -f security-report.json bandit-report.json
	@echo "🧹 Cleanup complete"

docs:
	cd docs && sphinx-build -b html . _build/html
	@echo "📚 Documentation built in docs/_build/html/"

run:
	python3 unified_ai_hunter.py --daily

run-batch:
	python3 automated_apply.py --batch 5

check-gmail:
	python3 test_gmail_auth.py

db-status:
	@echo "📊 Database Status:"
	@sqlite3 UNIFIED_AI_JOBS.db "SELECT COUNT(*) as total, COUNT(CASE WHEN applied=1 THEN 1 END) as applied FROM job_discoveries;" || echo "Database not found"

git-init:
	@if [ ! -d .git ]; then \
		git init; \
		git add .; \
		git commit -m "Initial commit: Career automation system with testing"; \
		echo "✅ Git repository initialized"; \
	else \
		echo "⚠️  Git repository already exists"; \
	fi

pre-commit:
	pre-commit install
	pre-commit run --all-files
	@echo "✅ Pre-commit hooks installed and run"

# Development workflow commands
dev-setup: install pre-commit
	@echo "🚀 Development environment ready!"

dev-check: lint test-unit security
	@echo "✅ All development checks passed!"

dev-commit: format lint test-unit
	git add -A
	git status
	@echo "Ready to commit! Use: git commit -m 'your message'"

# CI simulation
ci-local:
	@echo "🔄 Running local CI simulation..."
	make lint
	make test
	make coverage
	make security
	@echo "✅ Local CI simulation complete!"

# Version management
version:
	@echo "Career Automation System v1.0.0"

bump-patch:
	@echo "Bumping patch version..."
	# Would use bumpversion or similar tool here

bump-minor:
	@echo "Bumping minor version..."
	# Would use bumpversion or similar tool here

bump-major:
	@echo "Bumping major version..."
	# Would use bumpversion or similar tool here