"""
SQLAlchemy models for the application.
"""

from datetime import datetime, timezone
from typing import ClassVar

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


def utc_now():
    """Get current UTC datetime as timezone-aware."""
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    """User model for authentication."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    # Relationships
    entries = db.relationship(
        "Entry", backref="created_by", foreign_keys="Entry.created_by_user_id"
    )
    entries_updated = db.relationship(
        "Entry", backref="updated_by", foreign_keys="Entry.updated_by_user_id"
    )
    recurring_templates = db.relationship(
        "RecurringTaskTemplate",
        backref="created_by",
        foreign_keys="RecurringTaskTemplate.created_by_user_id",
    )
    recurring_templates_updated = db.relationship(
        "RecurringTaskTemplate",
        backref="updated_by",
        foreign_keys="RecurringTaskTemplate.updated_by_user_id",
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    def set_password(self, password: str) -> None:
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)


class Entry(db.Model):
    """Event or task entry."""

    __tablename__ = "entries"

    ENTRY_TYPE_EVENT: ClassVar[str] = "event"
    ENTRY_TYPE_TASK: ClassVar[str] = "task"
    ENTRY_TYPES: ClassVar[list[str]] = [ENTRY_TYPE_EVENT, ENTRY_TYPE_TASK]

    id = db.Column(db.Integer, primary_key=True)
    entry_type = db.Column(db.String(10), nullable=False)  # 'event' or 'task'
    title = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text, default="", nullable=False)
    location = db.Column(db.String(255), default="", nullable=False)

    # Time fields
    start_at = db.Column(db.DateTime, nullable=True)
    end_at = db.Column(db.DateTime, nullable=True)
    due_at = db.Column(db.DateTime, nullable=True)  # For tasks
    is_all_day = db.Column(db.Boolean, default=False, nullable=False)

    # Task-specific
    is_done = db.Column(db.Boolean, default=False, nullable=False)

    # Metadata
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Track if this entry was created from a recurring template
    recurring_template_id = db.Column(
        db.Integer, db.ForeignKey("recurring_task_templates.id"), nullable=True
    )
    recurring_template = db.relationship(
        "RecurringTaskTemplate",
        backref="entries",
        foreign_keys=[recurring_template_id],
    )

    __table_args__ = (
        db.Index("idx_entry_type", "entry_type"),
        db.Index("idx_entry_start_at", "start_at"),
        db.Index("idx_entry_due_at", "due_at"),
    )

    def __repr__(self) -> str:
        return f"<Entry {self.entry_type}: {self.title}>"


class RecurringTaskTemplate(db.Model):
    """Template for recurring weekly tasks."""

    __tablename__ = "recurring_task_templates"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text, default="", nullable=False)

    # Default settings
    default_weekday = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    default_time_start = db.Column(db.Time, nullable=True)
    default_time_end = db.Column(db.Time, nullable=True)

    is_active = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    # Metadata
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (
        db.Index("idx_recurring_active", "is_active"),
        db.Index("idx_recurring_weekday", "default_weekday"),
    )

    def __repr__(self) -> str:
        return f"<RecurringTaskTemplate {self.title}>"
