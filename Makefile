# Makefile for pysecop (Linux/macOS)
# Uses 'pip' for dependency management

.PHONY: install build test coverage example clean help

# Default target: Install dependencies
install:
	@echo "Installing dependencies with pip..."
	pip install .

install-dev:
	@echo "Installing dev dependencies..."
	pip install -e ".[dev]"

# Docker targets
build:
	@echo "Building Docker image (pysecop-dev)..."
	docker build -t pysecop-dev .

rebuild:
	@echo "Rebuilding Docker image from scratch..."
	docker build --no-cache -t pysecop-dev .

# Testing targets
test:
	@echo "Running tests with pytest..."
	pytest

coverage:
	@echo "Generating coverage report..."
	pytest --cov=pysecop --cov-report=html --cov-report=xml
	@echo "Coverage report generated in htmlcov/index.html"

# Run example script
example:
	@echo "Running example usage script..."
	python experiments/example_usage.py

# Cleanup
clean:
	@echo "Cleaning up temporary files..."
	rm -rf .pytest_cache .coverage htmlcov coverage.xml dist build *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Help
help:
	@echo "Available commands:"
	@echo "  install      : Install the package locally"
	@echo "  install-dev  : Install the package in editable mode with development dependencies"
	@echo "  build        : Build the Docker image"
	@echo "  rebuild      : Rebuild the Docker image without cache"
	@echo "  test         : Run tests using pytest"
	@echo "  coverage     : Run tests and generate coverage report"
	@echo "  example      : Run the example usage script from experiments"
	@echo "  clean        : Remove temporary files and build artifacts"
