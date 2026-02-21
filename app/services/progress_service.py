"""Progress service: log weight and get weight history."""
from app.models.progress_log import ProgressLog


def log_weight(session, user_id, weight_kg, date):
    """Add a weight log for the user on the given date. date can be date or datetime."""
    if hasattr(date, "date"):
        date = date.date()
    log = ProgressLog(user_id=user_id, weight_kg=float(weight_kg), logged_at=date)
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


def get_weight_logs(session, user_id):
    """Return all weight logs for this user, ordered by date (oldest first)."""
    return (
        session.query(ProgressLog)
        .filter(ProgressLog.user_id == user_id)
        .order_by(ProgressLog.logged_at.asc())
        .all()
    )