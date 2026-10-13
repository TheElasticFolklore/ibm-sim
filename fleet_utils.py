# fleet_utils.py
# Helpers for the nightly run. Every function here is called from fleet_report.py or
# verify.py; the five unreferenced helpers this file accumulated between 2013 and 2014
# (mean, is_due, format_percent, parse_service_date, chunk_list) were removed as dead code.

MILES_PER_KM = 0.621371                 # 1 mile = 1.609344 km, so this factor goes km -> miles


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles. Used by the nightly run for the UK partner report."""
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a number to one decimal place."""
    return f"{value:.1f}"