# Contributing to Gnit

Thank you for your interest in contributing to Gnit!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gnit.git
cd gnit
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

## Code Style

- Use Black for formatting: `black gnit/ tests/`
- Use isort for imports: `isort gnit/ tests/`
- Follow PEP 8 guidelines
- Max line length: 100 characters
- Add type hints to public functions

## Testing

Run tests before submitting:
```bash
pytest tests/ -v --cov=gnit
```

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

## Questions?

Open an issue for discussion before major changes.
