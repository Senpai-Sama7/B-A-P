# Contributing to AI Analytics Platform

Thank you for your interest in contributing to the AI Analytics Platform! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Poetry for dependency management
- PostgreSQL 14+ (for development)
- Redis 6+ (for caching)
- Git

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/ai-analytics-platform.git
   cd ai-analytics-platform
   ```

2. **Install Poetry (if not already installed):**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies:**
   ```bash
   poetry install --with dev
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

5. **Start local services (using Docker Compose):**
   ```bash
   docker-compose up -d postgres redis
   ```

6. **Run the application:**
   ```bash
   poetry run uvicorn src.main:app --reload
   ```

## Project Structure

```
ai-analytics-platform/
├── src/
│   ├── ai/              # AI/ML modules (GPT, forecasting, insights)
│   ├── api/             # API routes and middleware
│   ├── config/          # Configuration management
│   ├── core/            # Core utilities (database, cache, security)
│   ├── etl/             # ETL pipeline components
│   ├── models/          # Data models and schemas
│   ├── utils/           # Utility functions
│   └── main.py          # Application entry point
├── tests/               # Test suite
├── helm/                # Kubernetes Helm charts
├── scripts/             # Utility scripts
├── docs/                # Documentation
├── pyproject.toml       # Project metadata and dependencies
└── README.md            # Project readme
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clean, readable code
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/test_api.py
```

### 4. Lint and Format Code

```bash
# Format code with Black
poetry run black src tests

# Lint with Ruff
poetry run ruff check src tests

# Type check with mypy
poetry run mypy src
```

### 5. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git commit -m "feat: add data export functionality"
git commit -m "fix: resolve database connection timeout"
git commit -m "docs: update API documentation"
```

## Code Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://black.readthedocs.io/) for code formatting (line length: 100)
- Use type hints for all function signatures
- Write docstrings for all public functions and classes

### Code Quality

- Keep functions small and focused (single responsibility)
- Use meaningful variable and function names
- Avoid deep nesting (max 3-4 levels)
- Handle errors explicitly (don't use bare except)
- Use async/await for I/O operations
- Log important events and errors

### Example:

```python
from typing import Optional
from src.utils.logger import get_logger

logger = get_logger()

async def fetch_dataset(dataset_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a dataset by ID from the database.
    
    Args:
        dataset_id: Unique identifier for the dataset
        
    Returns:
        Dataset data or None if not found
        
    Raises:
        DatabaseError: If database connection fails
    """
    try:
        async with db_manager.session() as session:
            result = await session.execute(
                select(Dataset).where(Dataset.id == dataset_id)
            )
            return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Failed to fetch dataset {dataset_id}: {e}")
        raise DatabaseError(f"Dataset fetch failed: {e}")
```

## Testing

### Test Structure

- Unit tests: Test individual functions and classes
- Integration tests: Test component interactions
- E2E tests: Test complete workflows
- Performance tests: Test system under load

### Writing Tests

```python
import pytest
from src.etl.pipeline import ETLPipeline

@pytest.mark.asyncio
async def test_etl_pipeline_success():
    """Test successful ETL pipeline execution."""
    pipeline = ETLPipeline()
    request = PipelineRequest(dataset_id="test-123")
    
    await pipeline.run(request, user="test-user")
    
    # Verify results
    cache = await get_redis()
    status = await cache.get("etl:status:test-123")
    assert status == "completed"
```

### Running Tests

```bash
# All tests
poetry run pytest

# Specific test file
poetry run pytest tests/test_etl.py

# Specific test function
poetry run pytest tests/test_etl.py::test_etl_pipeline_success

# With coverage
poetry run pytest --cov=src --cov-report=term-missing

# With output
poetry run pytest -v -s
```

## Documentation

### Code Documentation

- Write clear docstrings for all public APIs
- Include parameter types, return types, and examples
- Document exceptions that can be raised
- Keep comments concise and meaningful

### API Documentation

- API documentation is auto-generated from code
- Access at `/docs` (Swagger UI) or `/redoc` (ReDoc)
- Update OpenAPI schemas when modifying endpoints

## Pull Request Process

### Before Submitting

1. ✅ All tests pass
2. ✅ Code is formatted and linted
3. ✅ New tests added for new functionality
4. ✅ Documentation updated
5. ✅ No merge conflicts with main branch

### Submitting a Pull Request

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request:**
   - Go to the repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template

3. **PR Description Should Include:**
   - What changed and why
   - How to test the changes
   - Any breaking changes
   - Screenshots (if UI changes)
   - Related issues

4. **Review Process:**
   - Maintainers will review your PR
   - Address any feedback
   - Keep your PR up to date with main

5. **After Approval:**
   - PR will be merged by a maintainer
   - Delete your feature branch

## Questions?

If you have questions or need help:

- Open an issue for bugs or feature requests
- Join our community chat (if available)
- Email the maintainers

Thank you for contributing! 🎉
