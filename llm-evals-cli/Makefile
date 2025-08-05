# Install core dependencies
install:
	pip install typer[all] requests pydantic pandas rich tabulate

# Install optional toxicity detection
install-toxicity:
	pip install torch detoxify --index-url https://download.pytorch.org/whl/cpu

# Install optional PII detection (may require system dependencies)
install-safety:
	pip install presidio-analyzer presidio-anonymizer spacy
	python -m spacy download en_core_web_sm

# Install everything (may fail on some systems due to build requirements)
install-all: install install-toxicity install-safety

# Development setup
dev:
	pip install pytest ruff

# Run tests
test:
	pytest -q

# Lint code
lint:
	ruff check .

# Format code
format:
	ruff format .

# Quick evaluation run
run:
	python -m evals.cli run --model llama3 --prompts prompts.csv --policy policy.json

# Clean up generated files
clean:
	rm -rf runs/* .pytest_cache __pycache__ **/__pycache__ **/*.pyc

.PHONY: install install-toxicity install-safety install-all dev test lint format run clean
