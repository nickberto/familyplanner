"""
Recurring task logic and materialization.
"""
from datetime import datetime, date, time, timedelta
from typing import List, Optional
from familyplanner.models import db, Entry, RecurringTaskTemplate
from familyplanner.domain.week import get_week_start, get_week_days, Weekday


def get_or_materialize_recurring_tasks(
    reference_date: date, 
    current_user_id: int
) -> List[Entry]:
    """
    Get recurring task instances for the given week.
    
    This materializes recurring task templates into concrete Entry instances
    for the specified week if they don't already exist.
    
    Args:
        reference_date: Any date in the desired week.
        current_user_id: User ID for attribution.
    
    Returns:
        List of Entry instances (created or existing) for the week.
    """
    week_start = get_week_start(reference_date)
    week_end = week_start + timedelta(days=6)
    
    # Get all active recurring task templates
    templates = RecurringTaskTemplate.query.filter_by(is_active=True).order_by(
        RecurringTaskTemplate.sort_order
    ).all()
    
    created_entries = []
    
    for template in templates:
        # Calculate the date for this template's weekday in this week
        target_date = week_start + timedelta(days=template.default_weekday)
        
        # Check if an entry already exists for this template date
        existing = Entry.query.filter(
            Entry.entry_type == Entry.ENTRY_TYPE_TASK,
            Entry.title == template.title,
            db.func.date(Entry.due_at) == target_date
        ).first()
        
        if existing:
            created_entries.append(existing)
        else:
            # Create a new entry from the template
            due_datetime = datetime.combine(target_date, template.default_time_start or time.min)
            
            entry = Entry(
                entry_type=Entry.ENTRY_TYPE_TASK,
                title=template.title,
                notes=template.notes,
                location="",
                start_at=None,
                end_at=None,
                due_at=due_datetime,
                is_all_day=False,
                is_done=False,
                created_by_user_id=current_user_id,
                updated_by_user_id=current_user_id,
            )
            db.session.add(entry)
            created_entries.append(entry)
    
    db.session.commit()
    return created_entries


def get_entries_for_week(reference_date: date) -> List[Entry]:
    """
    Get all entries (events and tasks) for the given week.
    
    Args:
        reference_date: Any date in the desired week.
    
    Returns:
        List of Entry instances sorted by date/time.
    """
    week_start = datetime.combine(get_week_start(reference_date), time.min)
    week_end = datetime.combine(
        get_week_start(reference_date) + timedelta(days=6),
        time.max
    )
    
    entries = Entry.query.filter(
        (Entry.start_at.between(week_start, week_end)) |
        (Entry.due_at.between(week_start, week_end)) |
        (Entry.end_at.between(week_start, week_end))
    ).order_by(Entry.start_at, Entry.due_at).all()
    
    return entries


def entries_by_weekday(entries: List[Entry]) -> dict:
    """
    Group entries by weekday (0=Monday, 6=Sunday).
    
    Args:
        entries: List of Entry instances.
    
    Returns:
        Dictionary mapping Weekday values to lists of entries.
    """
    grouped = {i: [] for i in range(7)}
    
    for entry in entries:
        dt = entry.start_at or entry.due_at or entry.end_at
        if dt:
            weekday = dt.date().weekday()
            grouped[weekday].append(entry)
    
    return grouped
