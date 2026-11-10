from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(value: datetime) -> datetime:
    """Normalise naive datetimes (e.g. from SQLite in tests) to aware UTC."""
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
