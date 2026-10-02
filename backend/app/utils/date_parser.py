import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Union, Optional

logger = logging.getLogger("careerloom.date_parser")


def parse_posting_date(raw_date: Union[str, int, float, None]) -> datetime:
    """
    Normalizes any raw date from various ATS feeds (Greenhouse, Lever, Ashby, custom)
    into a timezone-aware UTC datetime.
    """
    now = datetime.now(timezone.utc)
    if raw_date is None or raw_date == "":
        return now

    # 1. Numeric timestamp (seconds or milliseconds)
    if isinstance(raw_date, (int, float)):
        try:
            # Lever returns timestamps in milliseconds (> 1e11)
            ts = raw_date / 1000.0 if raw_date > 1e11 else float(raw_date)
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except Exception as e:
            logger.warning(f"Failed to parse numeric timestamp {raw_date}: {e}")
            return now

    # If numeric in string format
    if isinstance(raw_date, str) and raw_date.strip().isdigit():
        val = int(raw_date.strip())
        ts = val / 1000.0 if val > 1e11 else float(val)
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    # 2. String representation
    date_str = str(raw_date).strip()

    # Relative time strings
    lower_str = date_str.lower()
    if "just posted" in lower_str or "today" in lower_str or "hours ago" in lower_str or "minutes ago" in lower_str:
        return now
    if "yesterday" in lower_str:
        return now - timedelta(days=1)

    # Pattern: "X days ago" or "X day ago"
    days_match = re.search(r"(\d+)\s+day", lower_str)
    if days_match:
        days = int(days_match.group(1))
        return now - timedelta(days=days)

    # Pattern: "X weeks ago" or "X week ago"
    weeks_match = re.search(r"(\d+)\s+week", lower_str)
    if weeks_match:
        weeks = int(weeks_match.group(1))
        return now - timedelta(weeks=weeks)

    # Pattern: "X months ago" or "X month ago"
    months_match = re.search(r"(\d+)\s+month", lower_str)
    if months_match:
        months = int(months_match.group(1))
        return now - timedelta(days=months * 30)

    # 3. ISO format or standard date strings
    # Clean trailing 'Z' for python fromisoformat compatibility
    clean_iso = date_str
    if clean_iso.endswith("Z"):
        clean_iso = clean_iso[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(clean_iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        pass

    # Try common formats
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    logger.debug(f"Unable to parse date '{date_str}', defaulting to now")
    return now


def format_relative_date(dt: datetime) -> str:
    """
    Produces clean human-readable relative text (e.g. '2 days ago', 'Today', '3 weeks ago').
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    diff = now - dt

    if diff.total_seconds() < 0:
        return "Just posted"

    seconds = int(diff.total_seconds())
    days = diff.days

    if days == 0:
        if seconds < 3600:
            minutes = max(1, seconds // 60)
            return f"{minutes}m ago"
        hours = seconds // 3600
        return f"{hours}h ago"
    elif days == 1:
        return "Yesterday"
    elif days < 7:
        return f"{days}d ago"
    elif days < 30:
        weeks = days // 7
        return f"{weeks}w ago"
    elif days < 365:
        months = days // 30
        return f"{months}mo ago"
    else:
        years = days // 365
        return f"{years}y ago"
