# Family Planner

A minimal, shared weekly planner web app built with Python and Flask. All users can see and edit all entries without roles or permissions beyond login.

## Features

- **Shared Calendar**: All users see and can edit all events and tasks
- **Two Entry Types**:
  - Events: with time ranges (e.g., meetings, appointments)
  - Tasks: assigned to specific days, can be marked done
- **Recurring Weekly Tasks**: Create task templates that auto-materialize each week
- **Audit Trail**: Every change records who made it and when
- **Server-Rendered HTML**: Simple, secure, minimal JavaScript

## Tech Stack

- **Backend**: Python 3.11+, Flask
- **Database**: SQLite
- **Frontend**: Jinja2 templates, minimal CSS
- **Security**: Password hashing, CSRF protection, secure session cookies

## Project Structure

```
familyplanner/
├── config.py                 # Configuration (dev/test/prod)
├── app.py                    # App factory and initialization
├── models.py                 # SQLAlchemy models (User, Entry, RecurringTaskTemplate)
├── web/
│   ├── auth.py              # Authentication routes
│   └── calendar.py          # Calendar and planner routes
├── domain/
│   ├── week.py              # Week calculation and validation logic
│   └── recurring.py         # Recurring task materialization
├── templates/
│   ├── base.html            # Base template
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   └── calendar/
│       ├── week.html        # Main week view
│       ├── create_entry.html
│       ├── edit_entry.html
│       ├── create_recurring_template.html
│       └── edit_recurring_template.html
└── static/
    └── style.css            # Minimal styling
```

## Getting Started

### Install Dependencies

```bash
cd familyplanner
pip install -r requirements.txt
```

### Run Development Server

```bash
python wsgi.py
```

The app will start at `http://localhost:5000`.

### Create Database

The database is created automatically on first run. For a fresh database:

```bash
rm familyplanner.db
python wsgi.py
```

### Run Tests

```bash
pytest tests/ -v
```

## Usage

1. **Register**: Create a new account with username and password
2. **Login**: Access the shared planner
3. **View Week**: See all events and tasks for the current week
4. **Create Entry**: Add events or tasks
5. **Manage Tasks**: Mark tasks as done, edit, or delete
6. **Recurring Tasks**: Create templates for weekly recurring tasks

## Database Models

### User
- `username`: Unique username
- `password_hash`: Bcrypt hashed password
- `is_active`: Account status
- `created_at`: Registration timestamp

### Entry
- `entry_type`: "event" or "task"
- `title`, `notes`, `location`
- `start_at`, `end_at`: For events
- `due_at`: For tasks
- `is_done`: Task completion status
- `created_by_user_id`, `updated_by_user_id`: Audit trail
- `created_at`, `updated_at`: Timestamps

### RecurringTaskTemplate
- `title`, `notes`
- `default_weekday`: 0=Monday, 6=Sunday
- `default_time_start`, `default_time_end`: Optional times
- `is_active`: Enable/disable template
- `sort_order`: Display order
- `created_by_user_id`, `updated_by_user_id`: Audit trail
- `created_at`, `updated_at`: Timestamps

## Business Rules

- Everyone can see and edit all entries
- Events must have `end_at > start_at`
- Tasks can have optional time fields
- Recurring task templates materialize weekly (creates Entry instances)
- Changes track the user and timestamp
- Last write wins on conflicts (no concurrent editing logic)

## Configuration

Environment-based config:

```bash
ENV=development  # development, testing, production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///familyplanner.db
```

For production on Uberspace:
- Set `ENV=production`
- Store `SECRET_KEY` in environment or secrets file
- Use a proper WSGI server (uWSGI)
- Configure with supervisord

## Security

- Passwords hashed with Werkzeug
- CSRF protection enabled
- Secure session cookies
- Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- Input validation on all forms
- Output escaping in templates

## Limitations & Future Improvements

### Out of Scope (MVP)
- Real-time sync
- Drag and drop
- Complex recurrence rules
- Private calendars
- Role-based permissions
- External calendar integration

### Possible Enhancements
- Conflict detection
- Recurring task exceptions
- Task dependencies
- Categories/colors
- Search
- Mobile app

## License

MIT

## Development Notes

### Code Organization
- Keep route handlers thin
- No SQL in routes
- No business logic in templates
- Centralize week/date logic in `domain/week.py`
- Use `domain/recurring.py` for recurring task logic

### Best Practices
- Type hints in service/repository layers
- Clear function names
- Short docstrings
- Minimal dependencies
- Prefer standard library

## Deployment

See deployment instructions in the SPEC.md file for Uberspace setup with virtualenv, uWSGI, and supervisord.
