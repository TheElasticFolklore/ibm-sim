# fleet_utils.py
# Sammelbecken fuer Helfer seit 2013. Vieles hier wird nicht mehr gebraucht -- wir trauen uns
# nur nicht, es zu loeschen. (Catch-all helpers since 2013. Much of this is unused -- we just
# never dared to delete anything.)

MILES_PER_KM = 0.621371                 # 1 mile = 1.609344 km, so this factor goes km -> miles


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles. Used by the nightly run for the UK partner report."""
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a number to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: int) -> str:
    """Format an integer percentage, e.g. 80 -> '80%'."""
    return f"{value}%"


def mean(values: list[float]) -> float:
    """Return the arithmetic mean of values, or 0.0 if there are none."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def is_due(pct: float, threshold: float) -> bool:
    """Return True if wear percentage has reached the threshold."""
    return pct >= threshold


def parse_service_date(text: str) -> tuple[int, int, int] | None:
    """Parse a DD.MM.YYYY date into (year, month, day), or None if it is malformed."""
    parts = text.split(".")
    if len(parts) != 3:
        return None
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])
    return (year, month, day)


def chunk_list(items: list, size: int) -> list[list]:
    """Split items into consecutive chunks of the given size."""
    chunks = []
    current = []
    for item in items:
        current.append(item)
        if len(current) == size:
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks