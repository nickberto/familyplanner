"""
Tests for the Family Planner app.
"""

from datetime import date, datetime

import pytest

from familyplanner.app import create_app
from familyplanner.domain.week import (
    EventValidator,
    get_week_days,
    get_week_end,
    get_week_start,
)
from familyplanner.models import Entry, RecurringTaskTemplate, User, db


@pytest.fixture
def app():
    """Create and configure test app."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for tests
    app.config["REGISTRATION_ENABLED"] = True  # Enable registration for tests

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


class TestWeekLogic:
    """Test week calculation logic."""

    def test_get_week_start(self):
        """Test getting the Monday of a week."""
        # December 29, 2026 is a Saturday
        reference = date(2026, 12, 29)
        week_start = get_week_start(reference)
        assert week_start.weekday() == 0  # Monday
        assert week_start == date(2026, 12, 28)

    def test_get_week_end(self):
        """Test getting the Sunday of a week."""
        reference = date(2026, 12, 29)
        week_end = get_week_end(reference)
        assert week_end.weekday() == 6  # Sunday
        assert week_end == date(2027, 1, 3)

    def test_get_week_days(self):
        """Test getting all days in a week."""
        reference = date(2026, 12, 29)
        days = get_week_days(reference)
        assert len(days) == 7
        assert days[0].weekday() == 0  # Monday
        assert days[6].weekday() == 6  # Sunday


class TestWeekView:
    """Test week view rendering."""

    def test_highlights_current_day(self, client, app):
        """The current day should be highlighted in the week view."""
        with app.app_context():
            user = User(username="testuser")
            user.set_password("testpass123")
            db.session.add(user)
            db.session.commit()

        client.post("/auth/login", data={"username": "testuser", "password": "testpass123"})

        today = date.today()
        week_start = get_week_start(today)
        response = client.get(f"/week?date={week_start.isoformat()}")

        assert response.status_code == 200
        assert b'class="day-column today"' in response.data

class TestEventValidator:
    """Test event validation."""

    def test_valid_event_times(self):
        """Test valid event times."""
        start = datetime(2026, 5, 29, 10, 0)
        end = datetime(2026, 5, 29, 11, 0)
        is_valid, msg = EventValidator.validate_event_times(start, end)
        assert is_valid
        assert msg == ""

    def test_invalid_event_times_equal(self):
        """Test invalid event times (equal)."""
        start = datetime(2026, 5, 29, 10, 0)
        end = datetime(2026, 5, 29, 10, 0)
        is_valid, msg = EventValidator.validate_event_times(start, end)
        assert not is_valid
        assert msg != ""


class TestAuthentication:
    """Test user authentication."""

    def test_register(self, client, app):
        """Test user registration."""
        response = client.post(
            "/auth/register", data={"username": "testuser", "password": "testpass123"}
        )
        assert response.status_code == 302

        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            assert user is not None
            assert user.check_password("testpass123")

    def test_login(self, client, app):
        """Test user login."""
        # Register a user first
        with app.app_context():
            user = User(username="testuser")
            user.set_password("testpass123")
            db.session.add(user)
            db.session.commit()

        # Try to login
        response = client.post(
            "/auth/login", data={"username": "testuser", "password": "testpass123"}
        )
        assert response.status_code == 302

    def test_login_invalid_password(self, client, app):
        """Test login with invalid password."""
        # Register a user first
        with app.app_context():
            user = User(username="testuser")
            user.set_password("testpass123")
            db.session.add(user)
            db.session.commit()

        # Try to login with wrong password
        response = client.post(
            "/auth/login", data={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == 302


class TestEntryCreation:
    """Test entry creation."""

    def test_create_event(self, client, app):
        """Test creating an event."""
        # Register and login
        with app.app_context():
            user = User(username="testuser")
            user.set_password("testpass123")
            db.session.add(user)
            db.session.commit()

        client.post("/auth/login", data={"username": "testuser", "password": "testpass123"})

        # Create an event
        response = client.post(
            "/entry",
            data={
                "entry_type": "event",
                "title": "Test Event",
                "notes": "Test notes",
                "location": "Test location",
                "start_at": "2026-05-29T10:00",
                "end_at": "2026-05-29T11:00",
            },
        )
        assert response.status_code == 302

        with app.app_context():
            entry = Entry.query.filter_by(title="Test Event").first()
            assert entry is not None
            assert entry.entry_type == "event"


class TestRecurringTaskGeneration:
    """Test recurring task materialization and deduplication."""

    def test_materializes_recurring_task_entry(self, app):
        with app.app_context():
            user = User(username="testuser")
            user.set_password("testpass123")
            db.session.add(user)
            db.session.commit()

            template = RecurringTaskTemplate(
                title="Weekly Review",
                notes="Review tasks",
                default_weekday=0,
                default_time_start=None,
                created_by_user_id=user.id,
                updated_by_user_id=user.id,
            )
            db.session.add(template)
            db.session.commit()

            from familyplanner.domain.recurring import get_or_materialize_recurring_tasks

            entries = get_or_materialize_recurring_tasks(date(2026, 5, 27), user.id)
            assert len(entries) == 1
            entry = entries[0]
            assert entry.recurring_template_id == template.id
            assert entry.title == "Weekly Review"
            assert entry.due_at.date() == date(2026, 5, 25) or entry.due_at.date() == date(
                2026, 5, 27
            )

    def test_does_not_duplicate_when_moved_within_same_week(self, app):
        with app.app_context():
            user = User(username="testuser")
            user.set_password("testpass123")
            db.session.add(user)
            db.session.commit()

            template = RecurringTaskTemplate(
                title="Weekly Review",
                notes="Review tasks",
                default_weekday=0,
                default_time_start=None,
                created_by_user_id=user.id,
                updated_by_user_id=user.id,
            )
            db.session.add(template)
            db.session.commit()

            moved_entry = Entry(
                entry_type=Entry.ENTRY_TYPE_TASK,
                title="Weekly Review",
                notes="Review tasks",
                location="",
                due_at=datetime(2026, 5, 26, 9, 0),
                is_all_day=False,
                is_done=False,
                created_by_user_id=user.id,
                updated_by_user_id=user.id,
                recurring_template_id=template.id,
            )
            db.session.add(moved_entry)
            db.session.commit()

            from familyplanner.domain.recurring import get_or_materialize_recurring_tasks

            entries = get_or_materialize_recurring_tasks(date(2026, 5, 27), user.id)
            assert len(entries) == 1
            assert entries[0].id == moved_entry.id

    def test_sets_relationship_for_legacy_entry(self, app):
        with app.app_context():
            user = User(username="testuser")
            user.set_password("testpass123")
            db.session.add(user)
            db.session.commit()

            template = RecurringTaskTemplate(
                title="Weekly Review",
                notes="Review tasks",
                default_weekday=0,
                default_time_start=None,
                created_by_user_id=user.id,
                updated_by_user_id=user.id,
            )
            db.session.add(template)
            db.session.commit()

            legacy_entry = Entry(
                entry_type=Entry.ENTRY_TYPE_TASK,
                title="Weekly Review",
                notes="Review tasks",
                location="",
                due_at=datetime(2026, 5, 25, 9, 0),
                is_all_day=False,
                is_done=False,
                created_by_user_id=user.id,
                updated_by_user_id=user.id,
            )
            db.session.add(legacy_entry)
            db.session.commit()

            from familyplanner.domain.recurring import get_or_materialize_recurring_tasks

            entries = get_or_materialize_recurring_tasks(date(2026, 5, 27), user.id)
            assert len(entries) == 1
            assert entries[0].id == legacy_entry.id
            assert entries[0].recurring_template_id == template.id

    def test_creates_new_entry_for_next_week(self, app):
        with app.app_context():
            user = User(username="testuser")
            user.set_password("testpass123")
            db.session.add(user)
            db.session.commit()

            template = RecurringTaskTemplate(
                title="Weekly Review",
                notes="Review tasks",
                default_weekday=0,
                default_time_start=None,
                created_by_user_id=user.id,
                updated_by_user_id=user.id,
            )
            db.session.add(template)
            db.session.commit()

            previous_week_entry = Entry(
                entry_type=Entry.ENTRY_TYPE_TASK,
                title="Weekly Review",
                notes="Review tasks",
                location="",
                due_at=datetime(2026, 5, 18, 9, 0),
                is_all_day=False,
                is_done=False,
                created_by_user_id=user.id,
                updated_by_user_id=user.id,
                recurring_template_id=template.id,
            )
            db.session.add(previous_week_entry)
            db.session.commit()

            from familyplanner.domain.recurring import get_or_materialize_recurring_tasks

            entries = get_or_materialize_recurring_tasks(date(2026, 5, 27), user.id)
            assert len(entries) == 1
            assert entries[0].id != previous_week_entry.id
