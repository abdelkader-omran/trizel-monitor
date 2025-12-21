"""
src/utils/timestamps.py - Timezone-aware UTC timestamp utilities

Provides deterministic, timezone-aware UTC timestamps for the AUTO DZ ACT system.
"""

from datetime import datetime, timezone


def now_utc_iso() -> str:
    """
    Return current UTC time as timezone-aware ISO-8601 string.
    
    Returns:
        str: ISO-8601 formatted timestamp with timezone (e.g., "2025-12-21T22:30:15.123456+00:00")
    
    Examples:
        >>> timestamp = now_utc_iso()
        >>> "+00:00" in timestamp
        True
    """
    return datetime.now(timezone.utc).isoformat()
