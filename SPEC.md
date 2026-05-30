# SPEC.md — Collaborative Weekly Planner

## Goal
Build a minimal web app for a shared weekly planner using Python and Flask on Uberspace.
Keep it simple, secure, transparent, and easy to maintain.
No SPA. No PWA. Minimal dependencies.

## Core Rules
- All users can see all entries.
- All users can create, edit, and delete all entries.
- Every change must store and show `last_modified_by` and `last_modified_at`.
- Login is required so changes can be attributed to a user.

## Entry Types
There are two entry types:
- `event`
- `task`

Rules:
- `event` has a time range.
- `task` are assigned to a specific day of the week and can be marked as done
- Week view starts on Monday.

## Recurring Weekly Tasks
The app supports weekly recurring tasks such as:
- Clean bathroom
- Vacuum hallway
- Take out trash

Implementation:
- Store recurring task templates separately.
- Materialize concrete task instances per week on demand.
- Each entry explicitly links to its originating template via `recurring_template_id` to prevent duplication when entries are moved within the same week.

## MVP Features
- Login
- Week view (previous / current / next week)
- Create, edit, delete entries
- Mark tasks as done
- Show events and tasks in the same weekly view
- Manage recurring weekly task templates
- Show last editor and last update timestamp in the UI

## Non-Goals
- No roles or permissions beyond login
- No private calendars
- No real-time sync
- No drag and drop
- No complex recurrence rules beyond weekly templates
- No external calendar integration

## Tech Constraints
- Python 3.11+
- Flask, Flask-SQLAlchemy, Flask-Login
- Jinja templates, SQLite
- Server-rendered HTML, minimal CSS
- Uberspace deployment with virtualenv, uWSGI, supervisord

## Language
- User Interface: German
- Code: English (comments, docstrings)
- Database: UTF-8 encoding for international text support

## Architecture Rules
Small, explicit structure:
- `web/` for routes
- `domain/` for business logic
- `models.py` for data layer
- `templates/` for Jinja2 rendering
- `static/` for CSS

Mandatory rules:
- Use `create_app()`.
- Keep route handlers thin.
- No SQL in routes.
- No business logic in templates.
- Centralize week/date logic.
- Prefer clear code over clever abstractions.

## Data Model
### User
- id
- username
- password_hash
- is_active
- created_at

### Entry
- id
- entry_type
- title
- notes
- location
- start_at, end_at, due_at
- is_all_day, is_done
- created_by_user_id, created_at
- updated_by_user_id, updated_at
- recurring_template_id (nullable, links to origin template)

### RecurringTaskTemplate
- id
- title, notes
- default_weekday, default_time_start, default_time_end
- is_active, sort_order
- created_by_user_id, created_at
- updated_by_user_id, updated_at

## Business Rules
- Everyone sees everything.
- Everyone can edit everything.
- `event` requires `end_at > start_at`.
- `task` time fields are optional.
- Recurring weekly tasks must appear in each week.
- Weekly task completion must be stored per week.
- MVP conflict rule: `last write wins`.

## Security Rules
- Store `SECRET_KEY` outside the repo.
- Hash passwords securely.
- Enable CSRF protection for all write operations.
- Use secure session cookie settings.
- Disable debug mode in production.
- Set basic security headers.
- Escape output by default.

## Code Quality Rules
- Use type hints in service and repository layers.
- Keep functions small.
- Use explicit names.
- Add short docstrings to public functions.
- Avoid unnecessary dependencies.
- Prefer standard library when reasonable.

## Testing
Use pytest. Covered:
- Login and authentication
- Week calculation
- Event/task creation, update, deletion
- Recurring task materialization and deduplication
- Shared editing behavior
- Audit trail (last editor and timestamp)

## Code Quality
- **Ruff**: Fast linting with import sorting
- **Black**: Code formatting (line length: 100)
- **Bandit**: Security checks
- **Pytest**: Test runner
