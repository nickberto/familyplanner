"""
Domain logic for week calculations and date handling.
"""
from datetime import datetime, timedelta, date, time
from typing import Tuple, List
from enum import IntEnum


class Weekday(IntEnum):
    """Weekday constants (Monday=0, Sunday=6)."""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    
    @classmethod
    def from_iso(cls, iso_weekday: int) -> "Weekday":
        """Convert ISO weekday (Monday=1) to Weekday (Monday=0)."""
        return cls((iso_weekday - 1) % 7)
    
    def to_iso(self) -> int:
        """Convert to ISO weekday (Monday=1)."""
        return self.value + 1


def get_week_start(reference_date: date) -> date:
    """
    Get the Monday of the week containing the reference date.
    
    Args:
        reference_date: Any date in the desired week.
    
    Returns:
        The Monday of that week.
    """
    # weekday() returns 0=Monday, 6=Sunday
    days_back = reference_date.weekday()
    return reference_date - timedelta(days=days_back)


def get_week_end(reference_date: date) -> date:
    """
    Get the Sunday of the week containing the reference date.
    
    Args:
        reference_date: Any date in the desired week.
    
    Returns:
        The Sunday of that week.
    """
    week_start = get_week_start(reference_date)
    return week_start + timedelta(days=6)


def get_week_range(reference_date: date) -> Tuple[datetime, datetime]:
    """
    Get the week's datetime range (Monday 00:00 to Sunday 23:59:59).
    
    Args:
        reference_date: Any date in the desired week.
    
    Returns:
        Tuple of (start_datetime, end_datetime) in UTC.
    """
    start = datetime.combine(get_week_start(reference_date), time.min)
    end = datetime.combine(get_week_end(reference_date), time.max)
    return start, end


def get_week_days(reference_date: date) -> List[date]:
    """
    Get list of all dates in the week (Monday through Sunday).
    
    Args:
        reference_date: Any date in the desired week.
    
    Returns:
        List of 7 dates starting from Monday.
    """
    week_start = get_week_start(reference_date)
    return [week_start + timedelta(days=i) for i in range(7)]


def date_to_weekday(target_date: date) -> Weekday:
    """Convert a date to its Weekday value."""
    return Weekday.from_iso(target_date.isoweekday())


class EventValidator:
    """Validate event business rules."""
    
    @staticmethod
    def validate_event_times(start_at: datetime, end_at: datetime) -> Tuple[bool, str]:
        """
        Validate that end_at > start_at.
        
        Args:
            start_at: Event start time.
            end_at: Event end time.
        
        Returns:
            Tuple of (is_valid, error_message).
        """
        if end_at <= start_at:
            return False, "Event end time must be after start time"
        return True, ""


class TaskValidator:
    """Validate task business rules."""
    
    @staticmethod
    def validate_task(title: str) -> Tuple[bool, str]:
        """
        Validate task fields.
        
        Args:
            title: Task title.
        
        Returns:
            Tuple of (is_valid, error_message).
        """
        if not title or not title.strip():
            return False, "Task title cannot be empty"
        return True, ""
