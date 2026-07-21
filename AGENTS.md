# AGENTS.md

## Project overview
- This repository is a Flask web app for shared weekly planning.
- The app factory lives in [familyplanner/app.py](familyplanner/app.py) and registers the auth and calendar blueprints from [familyplanner/web](familyplanner/web).
- Domain logic and date/week behavior are in [familyplanner/domain](familyplanner/domain), while persistence lives in [familyplanner/models.py](familyplanner/models.py).
- UI templates are in [familyplanner/templates](familyplanner/templates).

## Working conventions
- Prefer small, focused changes that match the existing Flask blueprint structure.
- Keep behavior changes covered by tests in [tests](tests).
- Follow the existing style settings from [pyproject.toml](pyproject.toml) and the quality script in [scripts/quality-check.sh](scripts/quality-check.sh).
- For deployment-related changes, update [DEPLOYMENT.md](DEPLOYMENT.md) and [supervisord.conf](supervisord.conf) together when relevant.

## Common commands
- Run the test suite: `pytest tests/ -v`
- Run the full quality checks: `bash scripts/quality-check.sh`
- Start the app locally: `python wsgi.py`

## Notes for agents
- The app uses environment-based configuration via [familyplanner/config.py](familyplanner/config.py).
- The default development flow expects a local SQLite database and a working Flask app entrypoint.
- When changing routes, forms, or templates, verify the relevant tests and adjust them if the behavior intentionally changes.
