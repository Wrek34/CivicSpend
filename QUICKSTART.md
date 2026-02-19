# 🏃 Development Quickstart

Get started with Gnit development in 5 minutes.

## Prerequisites

- Python 3.11 or higher
- Git
- GitHub account

## Setup (First Time)

### 1. Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Install package in editable mode
pip install -e .
```

### 3. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.11+

# Check gnit package
python -c "import gnit; print(gnit.__version__)"  # Should print 0.1.0-dev
```

## Week 1: Database Setup

### Create Database Schema

Create `gnit/db/schema.sql`:

```sql
-- Run manifest (tracks pipeline executions)
CREATE TABLE run_manifest (
    run_id TEXT PRIMARY KEY,
    run_timestamp TIMESTAMP,
    filters_json TEXT,
    row_count_raw INTEGER,
    model_artifact_path TEXT,
    config_hash TEXT,
    status TEXT
);

-- Raw awards (immutable storage)
CREATE TABLE raw_awards (
    run_id TEXT,
    award_id TEXT,
    recipient_name TEXT,
    recipient_duns TEXT,
    recipient_uei TEXT,
    awarding_agency_name TEXT,
    award_type TEXT,
    action_date DATE,
    obligation_amount DECIMAL(18,2),
    PRIMARY KEY (run_id, award_id)
);
```

### Create Database Connection

Create `gnit/db/connection.py`:

```python
import duckdb
from pathlib import Path

DB_PATH = Path("data/gnit.duckdb")

def get_connection():
    """Get DuckDB connection."""
    DB_PATH.parent.mkdir(exist_ok=True)
    return duckdb.connect(str(DB_PATH))

def init_database():
    """Initialize database with schema."""
    conn = get_connection()
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path) as f:
        conn.execute(f.read())
    conn.close()
```

### Test Database

Create `tests/test_db.py`:

```python
from gnit.db.connection import get_connection, init_database

def test_database_creation():
    init_database()
    conn = get_connection()
    
    # Verify tables exist
    tables = conn.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in tables]
    
    assert "run_manifest" in table_names
    assert "raw_awards" in table_names
    
    conn.close()
```

Run test:
```bash
pytest tests/test_db.py -v
```

## Daily Development Workflow

### 1. Start Your Day

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Edit files, write code, add tests.

### 3. Test Your Changes

```bash
# Run specific test
pytest tests/test_your_module.py -v

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=gnit --cov-report=html
```

### 4. Format Code

```bash
# Format with Black
black gnit/ tests/

# Sort imports
isort gnit/ tests/

# Check linting
flake8 gnit/ tests/
```

### 5. Commit Changes

```bash
# Stage changes
git add .

# Commit with conventional commit message
git commit -m "feat(module): add feature description"

# Push to GitHub
git push origin feature/your-feature-name
```

### 6. Create Pull Request

Go to GitHub and create a pull request from your feature branch to `main`.

## Useful Commands

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_ingest.py

# Run specific test
pytest tests/test_ingest.py::test_api_client -v

# Run with coverage
pytest --cov=gnit --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

### Code Quality

```bash
# Format code
black gnit/ tests/

# Sort imports
isort gnit/ tests/

# Lint
flake8 gnit/ tests/

# Type check
mypy gnit/
```

### Git

```bash
# Check status
git status

# View changes
git diff

# View commit history
git log --oneline

# Switch branches
git checkout main
git checkout -b feature/new-feature

# Undo changes (careful!)
git checkout -- filename.py
```

### Python

```bash
# Run Python file
python gnit/cli/main.py

# Interactive Python
python
>>> import gnit
>>> gnit.__version__

# Install package in editable mode
pip install -e .

# Uninstall package
pip uninstall gnit
```

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError`:
```bash
# Reinstall in editable mode
pip install -e .
```

### Virtual Environment Issues

If commands not found:
```bash
# Make sure venv is activated
# You should see (venv) in your prompt

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Database Locked

If DuckDB says database is locked:
```python
# Make sure to close connections
conn = get_connection()
# ... do work ...
conn.close()  # Always close!
```

### Test Failures

If tests fail:
```bash
# Run with verbose output
pytest tests/ -v -s

# Run specific failing test
pytest tests/test_module.py::test_function -v -s
```

## Week 1 Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] Database schema created (`gnit/db/schema.sql`)
- [ ] Database connection module (`gnit/db/connection.py`)
- [ ] Database test passing (`tests/test_db.py`)
- [ ] API client started (`gnit/ingest/api_client.py`)
- [ ] CLI command started (`gnit/cli/main.py`)
- [ ] First feature branch created
- [ ] First commit pushed to GitHub
- [ ] BUILD_LOG.md updated

## Resources

- **Documentation**: See `docs/INDEX.md`
- **Implementation Guide**: See `docs/IMPLEMENTATION_CHECKLIST.md`
- **Quick Reference**: See `docs/QUICK_REFERENCE.md`
- **Specification**: See `docs/SPECIFICATION.md`

## Getting Help

1. Check documentation in `docs/`
2. Review `docs/QUICK_REFERENCE.md` for commands
3. Check `docs/RISK_REGISTER.md` for known issues
4. Review `docs/DECISION_LOG.md` for rationale

## Next Steps

Follow `docs/IMPLEMENTATION_CHECKLIST.md` for detailed day-by-day tasks!

---

**Happy coding! 🚀**

