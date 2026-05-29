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
The app must support weekly recurring tasks such as:
- Clean bathroom
- Vacuum hallway
- Take out trash

Use a simple model:
- Store recurring task templates separately.
- Materialize concrete task instances per week, while opening the current week the firs time
- Weekly task instances can be checked off or edited without mutating past weeks unexpectedly.

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
- Flask
- Jinja templates
- SQLite
- Server-rendered HTML
- Minimal CSS
- Very little or no JavaScript
- Uberspace deployment with virtualenv, uWSGI, and supervisord

## Language
- User Interface: German
- Code: English (comments, docstrings)
- Database: UTF-8 encoding for international text support

## Architecture Rules
Use a small, explicit structure:
- `web/` for routes and forms
- `domain/` for business logic and time rules
- `persistence/` for database access
- `templates/` for rendering
- `static/` for CSS/JS

Mandatory rules:
- Use `create_app()`.
- Keep route handlers thin.
- Do not put SQL in routes.
- Do not put business logic in templates.
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
- start_at
- end_at
- due_at
- is_all_day
- is_done
- created_by_user_id
- created_at
- updated_by_user_id
- updated_at

### RecurringTaskTemplate
- id
- title
- notes
- default_weekday
- default_time_start
- default_time_end
- is_active
- sort_order
- created_by_user_id
- created_at
- updated_by_user_id
- updated_at

### Optional: RecurringTaskInstance
Use if weekly materialization is persisted explicitly.

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
Use pytest.
Minimum coverage should include:
- login
- week calculation
- event validation
- task creation/update
- recurring weekly task materialization
- permission model behavior (shared editing)
- last editor / timestamp updates

## Delivery Order
Claude Code should implement in this order:
1. project structure
2. app factory and config
3. auth and base models
4. domain rules and week logic
5. CRUD for events and tasks
6. recurring weekly tasks
7. templates and week view
8. security hardening
9. tests
10. README and deployment files

## Claude Code Constraints
- Do not add features outside this spec.
- Do not introduce heavy libraries without strong justification.
- Do not build a SPA.
- Do not add roles/ACL logic.
- Keep the code readable and boring.
- For each major change, explain: purpose, design choice, and open questions.
