"""
Calendar and planner routes.
"""
from datetime import datetime, date, timedelta, time
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from familyplanner.models import db, Entry, RecurringTaskTemplate, utc_now
from familyplanner.domain.week import get_week_start, get_week_range
from familyplanner.domain.recurring import get_entries_for_week, entries_by_weekday, get_or_materialize_recurring_tasks, get_active_recurring_templates

bp = Blueprint("calendar", __name__, url_prefix="/")


@bp.route("/")
def index():
    """Redirect to the calendar week view."""
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    return redirect(url_for("calendar.week"))


@bp.route("/week")
@login_required
def week():
    """Display the current week view."""
    reference_date_str = request.args.get("date")
    if reference_date_str:
        try:
            reference_date = datetime.strptime(reference_date_str, "%Y-%m-%d").date()
        except ValueError:
            reference_date = date.today()
    else:
        reference_date = date.today()
    
    # Materialize recurring tasks for this week
    get_or_materialize_recurring_tasks(reference_date, current_user.id)
    
    # Get all entries for this week
    entries = get_entries_for_week(reference_date)
    grouped = entries_by_weekday(entries)
    
    # Navigation
    week_start = get_week_start(reference_date)
    prev_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)
    
    return render_template(
        "calendar/week.html",
        reference_date=reference_date,
        week_start=week_start,
        entries=entries,
        grouped_entries=grouped,
        recurring_templates=get_active_recurring_templates(),
        prev_week=prev_week,
        next_week=next_week,
        current_user=current_user,
        timedelta=timedelta,
    )


@bp.route("/entry", methods=["GET", "POST"])
@login_required
def create_entry():
    """Create a new entry (event or task)."""
    if request.method == "POST":
        entry_type = request.form.get("entry_type", "").strip()
        title = request.form.get("title", "").strip()
        notes = request.form.get("notes", "").strip()
        location = request.form.get("location", "").strip()
        
        # Validation
        if not entry_type or entry_type not in Entry.ENTRY_TYPES:
            flash("Ungültiger Eintragstyp", "error")
            return redirect(url_for("calendar.week"))
        
        if not title:
            flash("Titel ist erforderlich", "error")
            return redirect(url_for("calendar.week"))
        
        # Parse datetime fields based on type
        if entry_type == Entry.ENTRY_TYPE_EVENT:
            start_str = request.form.get("start_at")
            end_str = request.form.get("end_at")
            
            if not start_str or not end_str:
                flash("Start- und Endzeit sind erforderlich für Ereignisse", "error")
                return redirect(url_for("calendar.week"))
            
            try:
                start_at = datetime.fromisoformat(start_str)
                end_at = datetime.fromisoformat(end_str)
                
                if end_at <= start_at:
                    flash("Endzeit muss nach Startzeit liegen", "error")
                    return redirect(url_for("calendar.week"))
            except ValueError:
                flash("Ungültiges Datetime-Format", "error")
                return redirect(url_for("calendar.week"))
            
            entry = Entry(
                entry_type=Entry.ENTRY_TYPE_EVENT,
                title=title,
                notes=notes,
                location=location,
                start_at=start_at,
                end_at=end_at,
                created_by_user_id=current_user.id,
                updated_by_user_id=current_user.id,
            )
        else:  # task
            due_str = request.form.get("due_at")
            if due_str:
                try:
                    due_at = datetime.fromisoformat(due_str)
                except ValueError:
                    flash("Invalid datetime format", "error")
                    return redirect(url_for("calendar.week"))
            else:
                due_at = None
            
            entry = Entry(
                entry_type=Entry.ENTRY_TYPE_TASK,
                title=title,
                notes=notes,
                location=location,
                due_at=due_at,
                created_by_user_id=current_user.id,
                updated_by_user_id=current_user.id,
            )
        
        db.session.add(entry)
        db.session.commit()
        flash("Eintrag erfolgreich erstellt", "success")
        return redirect(url_for("calendar.week"))
    
    return render_template("calendar/create_entry.html")


@bp.route("/entry/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
    """Edit an existing entry."""
    entry = Entry.query.get_or_404(entry_id)
    
    if request.method == "POST":
        entry.title = request.form.get("title", "").strip()
        entry.notes = request.form.get("notes", "").strip()
        entry.location = request.form.get("location", "").strip()
        entry.updated_by_user_id = current_user.id
        entry.updated_at = utc_now()
        
        if entry.entry_type == Entry.ENTRY_TYPE_EVENT:
            start_str = request.form.get("start_at")
            end_str = request.form.get("end_at")
            
            if start_str and end_str:
                try:
                    start_at = datetime.fromisoformat(start_str)
                    end_at = datetime.fromisoformat(end_str)
                    
                    if end_at <= start_at:
                        flash("Endzeit muss nach Startzeit liegen", "error")
                        return redirect(url_for("calendar.week"))
                    
                    entry.start_at = start_at
                    entry.end_at = end_at
                except ValueError:
                    flash("Ungültiges Datetime-Format", "error")
                    return redirect(url_for("calendar.week"))
        else:  # task
            due_str = request.form.get("due_at")
            if due_str:
                try:
                    entry.due_at = datetime.fromisoformat(due_str)
                except ValueError:
                    flash("Ungültiges Datetime-Format", "error")
                    return redirect(url_for("calendar.week"))
        
        db.session.commit()
        flash("Eintrag erfolgreich aktualisiert", "success")
        return redirect(url_for("calendar.week"))
    
    return render_template("calendar/edit_entry.html", entry=entry)


@bp.route("/entry/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_entry(entry_id):
    """Delete an entry."""
    entry = Entry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash("Eintrag erfolgreich gelöscht", "success")
    return redirect(url_for("calendar.week"))


@bp.route("/entry/<int:entry_id>/toggle-done", methods=["POST"])
@login_required
def toggle_entry_done(entry_id):
    """Toggle task completion status."""
    entry = Entry.query.get_or_404(entry_id)
    
    if entry.entry_type != Entry.ENTRY_TYPE_TASK:
        flash("Nur Aufgaben können als erledigt markiert werden", "error")
        return redirect(url_for("calendar.week"))
    
    entry.is_done = not entry.is_done
    entry.updated_by_user_id = current_user.id
    entry.updated_at = utc_now()
    db.session.commit()
    
    flash(f"Aufgabe markiert als {'erledigt' if entry.is_done else 'nicht erledigt'}", "success")
    return redirect(url_for("calendar.week"))


@bp.route("/recurring-template", methods=["GET", "POST"])
@login_required
def create_recurring_template():
    """Create a new recurring task template."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        notes = request.form.get("notes", "").strip()
        weekday = request.form.get("weekday", "")
        time_start_str = request.form.get("default_time_start", "").strip()
        time_end_str = request.form.get("default_time_end", "").strip()
        
        if not title:
            flash("Titel ist erforderlich", "error")
            return redirect(url_for("calendar.week"))
        
        if not weekday:
            flash("Wochentag ist erforderlich", "error")
            return redirect(url_for("calendar.week"))
        
        try:
            weekday_int = int(weekday)
            if not 0 <= weekday_int <= 6:
                raise ValueError
        except ValueError:
            flash("Ungültiger Wochentag", "error")
            return redirect(url_for("calendar.week"))
        
        template = RecurringTaskTemplate(
            title=title,
            notes=notes,
            default_weekday=weekday_int,
            created_by_user_id=current_user.id,
            updated_by_user_id=current_user.id,
        )
        db.session.add(template)
        db.session.commit()
        
        flash("Wiederkehrende Aufgabe erfolgreich erstellt", "success")
        return redirect(url_for("calendar.week"))
    
    return render_template("calendar/create_recurring_template.html")


@bp.route("/recurring-template/<int:template_id>/edit", methods=["GET", "POST"])
@login_required
def edit_recurring_template(template_id):
    """Edit a recurring task template."""
    template = RecurringTaskTemplate.query.get_or_404(template_id)
    
    if request.method == "POST":
        template.title = request.form.get("title", "").strip()
        template.notes = request.form.get("notes", "").strip()
        
        weekday = request.form.get("weekday", "")
        try:
            weekday_int = int(weekday)
            if not 0 <= weekday_int <= 6:
                raise ValueError
            template.default_weekday = weekday_int
        except ValueError:
            flash("Ungültiger Wochentag", "error")
            return redirect(url_for("calendar.week"))
        
        template.is_active = request.form.get("is_active") == "on"
        template.updated_by_user_id = current_user.id
        template.updated_at = utc_now()
        
        db.session.commit()
        flash("Wiederkehrende Aufgabe erfolgreich aktualisiert", "success")
        return redirect(url_for("calendar.week"))
    
    return render_template("calendar/edit_recurring_template.html", template=template)


@bp.route("/recurring-template/<int:template_id>/delete", methods=["POST"])
@login_required
def delete_recurring_template(template_id):
    """Delete a recurring task template."""
    template = RecurringTaskTemplate.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    flash("Wiederkehrende Aufgabe erfolgreich gelöscht", "success")
    return redirect(url_for("calendar.week"))
