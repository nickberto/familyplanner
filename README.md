# Family Planner

A minimal, shared weekly planner web app. All users can see and edit all entries without roles or permissions beyond login.

See [SPEC.md](SPEC.md) for full requirements and design.

## Quick Start

### Install & Run

```bash
pip install -r requirements.txt
python wsgi.py
```

App runs at `http://localhost:5000`. Database created automatically on first run.

### Reset Database

```bash
rm familyplanner.db
python wsgi.py
```

## Development

### Testing

```bash
pytest tests/ -v
```

### Code Quality

Run all checks:

```bash
bash scripts/quality-check.sh
```

Individual tools:

```bash
ruff check familyplanner tests          # Lint
black familyplanner tests               # Format
black --check familyplanner tests       # Check format
bandit -r familyplanner                 # Security
```

See `pyproject.toml` for tool configuration.

### Project Structure

See [SPEC.md — Architecture Rules](SPEC.md#architecture-rules) for folder layout and design principles.

### Configuration

Environment variables (see `config.py`):
- `ENV`: development, testing, production
- `SECRET_KEY`: Flask secret
- `DATABASE_URL`: SQLite path
- `REGISTRATION_ENABLED`: Enable user registration (default: True)

## Documentation

- [SPEC.md](SPEC.md) — Requirements, design, data model, business rules
- [DEPLOYMENT.md](DEPLOYMENT.md) — Production setup on Uberspace
- [REQUESTS.md](REQUESTS.md) — Active improvement requests

## License

MIT License. You can use, copy, modify, and distribute this code. It is provided "as is", without warranty or guarantee of any kind. You are responsible for anything you do with it.

## AI Notice

Parts of this project and documentation were created with AI assistance.