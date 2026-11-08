from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return the current UTC timestamp.

    Returns:
        A timezone-aware datetime set to now in UTC.
    """
    return datetime.now(UTC)
