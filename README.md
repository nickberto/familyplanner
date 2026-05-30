# Family Planner

A minimal, shared weekly planner web app. All users can see and edit all entries without roles or permissions beyond login.

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Development Server

```bash
python wsgi.py
```

App runs at `http://localhost:5000`. Database created automatically on first run.

### Reset Database

```bash
rm familyplanner.db
python wsgi.py
```

## Testing

```bash
pytest tests/ -v
```

## Code Quality

Run all checks (linting, formatting, security, tests):

```bash
bash scripts/quality-check.sh
```

Or run individual tools:

```bash
# Linting
ruff check familyplanner tests

# Format check
black --check familyplanner tests

# Auto-format code
black familyplanner tests

# Security checks
bandit -r familyplanner
```

Tools:
- **Ruff** — Fast Python linter with import sorting
- **Black** — Code formatter (line length: 100)
- **Bandit** — Security checks
- **Pytest** — Test runner configured in `pyproject.toml`

## Development

### Project Structure

```
familyplanner/
├── config.py              # Dev/test/prod config
├── app.py                 # App factory
├── models.py              # SQLAlchemy models
├── web/
│   ├── auth.py           # Auth routes
│   └── calendar.py       # Calendar routes
├── domain/
│   ├── week.py           # Week logic
│   └── recurring.py      # Recurring tasks
└── templates/            # Jinja2 templates
```

### Code Organization

- Route handlers in `web/` are thin
- Business logic in `domain/`
- No SQL in routes
- Use type hints
- Minimize dependencies

### Models

- **User**: username, password_hash, is_active
- **Entry**: event/task, title, notes, location, times, is_done, audit trail, recurring_template_id (nullable, links to origin template)
- **RecurringTaskTemplate**: title, weekday, times, is_active, sort_order, audit trail

### Configuration

Environment variables (see `config.py`):
- `ENV`: development, testing, production
- `SECRET_KEY`: Flask secret
- `DATABASE_URL`: SQLite path
- `REGISTRATION_ENABLED`: Enable user registration (default: False)

### Key Features

- Events (start/end times) and Tasks (due date)
- Recurring task templates auto-materialize weekly with explicit linkage to prevent duplication
- Audit trail (who, when for each change)
- German UI with locale-aware date formatting
- CSRF protection, secure cookies, password hashing

## Deployment

See `SPEC.md` for production setup (Uberspace, uWSGI, supervisord)
