# Contributing to CivicSpend

Thank you for your interest in contributing to CivicSpend!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/civicspend.git
cd civicspend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .
```

4. Initialize database:
```bash
civicspend init
```

## Code Style

- Use Black for formatting: `black civicspend/ tests/`
- Use isort for imports: `isort civicspend/ tests/`
- Follow PEP 8 guidelines
- Max line length: 100 characters
- Add type hints to public functions
- Write docstrings (Google style)

## Testing

Run tests before submitting:
```bash
pytest tests/ -v --cov=civicspend
```

Target coverage: >= 70%

## Important Constraints

### Language Guidelines
- **NEVER** use: "fraud", "corruption", "suspicious"
- **ALWAYS** use: "change", "anomaly", "outlier", "spike", "deviation"
- This is NOT fraud detection

### Evidence Requirements
- Every anomaly MUST link to source awards
- Include award IDs, amounts, agencies
- No speculation in narratives

## Commit Messages

Use conventional commits:
- `feat(module): add new feature`
- `fix(module): fix bug`
- `docs(module): update documentation`
- `test(module): add tests`
- `refactor(module): refactor code`

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Add tests
4. Run tests and linting
5. Commit with descriptive messages
6. Push and create a pull request
7. Ensure CI passes

## Questions?

Open an issue for discussion before major changes.
