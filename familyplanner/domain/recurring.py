"""
Recurring task logic and materialization.
"""

from datetime import date, datetime, time, timedelta
from typing import List

from familyplanner.domain.week import get_week_start
from familyplanner.models import Entry, RecurringTaskTemplate, db, utc_now


def get_or_materialize_recurring_tasks(
    reference_date: date, current_user_id: int, today: date | None = None
) -> List[Entry]:
    """
    Get recurring task instances for the given week.

    This materializes recurring task templates into concrete Entry instances
    for the specified week if they don't already exist.

    Args:
        reference_date: Any date in the desired week.
        current_user_id: User ID for attribution.
        today: The current date for moving overdue tasks in the current week.

    Returns:
        List of Entry instances (created or existing) for the week.
    """
    if today is None:
        today = date.today()

    week_start = get_week_start(reference_date)
    week_end = week_start + timedelta(days=6)
    week_start_dt = datetime.combine(week_start, time.min)
    week_end_dt = datetime.combine(week_end, time.max)
    is_current_week = week_start <= today <= week_end

    # Get all active recurring task templates
    templates = (
        RecurringTaskTemplate.query.filter_by(is_active=True)
        .order_by(RecurringTaskTemplate.sort_order)
        .all()
    )

    created_entries = []

    for template in templates:
        # Calculate the date for this template's weekday in this week
        target_date = week_start + timedelta(days=template.default_weekday)
        effective_date = today if is_current_week and target_date < today else target_date

        # Prefer explicit recurring-template relation for existing entries in this week.
        existing = Entry.query.filter(
            Entry.recurring_template_id == template.id,
            Entry.due_at >= week_start_dt,
            Entry.due_at <= week_end_dt,
        ).first()

        if existing:
            if (
                is_current_week
                and not existing.is_done
                and existing.due_at
                and existing.due_at.date() < today
            ):
                existing_due_time = existing.due_at.time()
                existing.due_at = datetime.combine(today, existing_due_time)
                existing.updated_by_user_id = current_user_id
                existing.updated_at = utc_now()
                db.session.add(existing)

            created_entries.append(existing)
            continue

        # Fallback for older entries created before the recurring link existed.
        fallback = Entry.query.filter(
            Entry.recurring_template_id.is_(None),
            Entry.entry_type == Entry.ENTRY_TYPE_TASK,
            Entry.title == template.title,
            Entry.created_by_user_id == current_user_id,
            db.func.date(Entry.due_at) == target_date,
        ).first()

        if fallback:
            if (
                is_current_week
                and not fallback.is_done
                and fallback.due_at
                and fallback.due_at.date() < today
            ):
                fallback_time = fallback.due_at.time()
                fallback.due_at = datetime.combine(today, fallback_time)

            fallback.recurring_template_id = template.id
            db.session.add(fallback)
            created_entries.append(fallback)
            continue

        # Create a new entry from the template
        due_datetime = datetime.combine(effective_date, template.default_time_start or time.min)

        # Do not create new recurring entries in the past (unless we're in the current week
        # where we intentionally move overdue instances to today).
        if due_datetime.date() < today and not is_current_week:
            continue

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
            recurring_template_id=template.id,
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
    week_end = datetime.combine(get_week_start(reference_date) + timedelta(days=6), time.max)

    entries = (
        Entry.query.filter(
            (Entry.start_at.between(week_start, week_end))
            | (Entry.due_at.between(week_start, week_end))
            | (Entry.end_at.between(week_start, week_end))
        )
        .order_by(Entry.start_at, Entry.due_at)
        .all()
    )

    return entries


def move_overdue_tasks_to_today(current_user_id: int, today: date | None = None) -> None:
    """
    Move all incomplete tasks with due dates in the past to today.
    
    This ensures that incomplete tasks that have passed their due date
    are automatically rescheduled to today, keeping the task list current.
    
    Args:
        current_user_id: User ID for attribution when updating tasks.
        today: The current date to use as the target date. Defaults to date.today().
    """
    if today is None:
        today = date.today()
    
    today_dt = datetime.combine(today, time.min)
    yesterday_dt = today_dt - timedelta(seconds=1)  # End of yesterday
    
    # Find all incomplete tasks with due_at in the past
    overdue_tasks = Entry.query.filter(
        Entry.entry_type == Entry.ENTRY_TYPE_TASK,
        Entry.is_done == False,
        Entry.due_at.isnot(None),
        Entry.due_at <= yesterday_dt
    ).all()
    
    for task in overdue_tasks:
        # Preserve the original time, just move the date to today
        original_time = task.due_at.time() if task.due_at else time(12, 0)
        task.due_at = datetime.combine(today, original_time)
        task.updated_by_user_id = current_user_id
        task.updated_at = utc_now()
        db.session.add(task)
    
    if overdue_tasks:
        db.session.commit()


def entries_by_weekday(entries: List[Entry]) -> dict:
    """
    Group entries by weekday (0-6 = Mon-Sun).

    Args:
        entries: List of Entry instances.

    Returns:
        Dictionary with weekday as key and list of entries as value.
    """
    from familyplanner.domain.week import date_to_weekday

    grouped = {i: [] for i in range(7)}
    for entry in entries:
        if entry.due_at:
            weekday = date_to_weekday(entry.due_at.date()).value
        elif entry.start_at:
            weekday = date_to_weekday(entry.start_at.date()).value
        else:
            continue
        grouped[weekday].append(entry)

    return grouped


def get_active_recurring_templates() -> List[RecurringTaskTemplate]:
    """
    Get all active recurring task templates, sorted by sort_order.

    Returns:
        List of active RecurringTaskTemplate instances.
    """
    return (
        RecurringTaskTemplate.query.filter_by(is_active=True)
        .order_by(RecurringTaskTemplate.sort_order)
        .all()
    )
