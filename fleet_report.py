# fleet_report.py
# Prints the nightly fleet-health summary for Vossberg Mobility.
# Written in 2014. Runs every morning. Never cleaned up.

from km_wachter import wear_percent, needs_service, SERVICE_INTERVAL_KM
from config_loader import load_settings, get_setting
from log_util import log, flush_log
import fleet_utils


def car_wear(car: dict) -> float | None:
    """Return the car's wear as a percentage, or None if it has no service reading."""
    if "last_service_km" not in car:
        return None
    return wear_percent(car["odometer"] - car["last_service_km"], SERVICE_INTERVAL_KM)


def fleet_summary(fleet: list[dict]) -> dict:
    """Return fleet size, how many cars are due, and average wear across the fleet.

    Cars with no service reading are left out of the average rather than counted
    as 0% worn, which would make the fleet look healthier than it really is.
    """
    wears = [w for w in (car_wear(car) for car in fleet) if w is not None]
    due = sum(1 for car in fleet if needs_service(car))
    average = sum(wears) / len(wears) if wears else 0
    return {"count": len(fleet), "due": due, "average_wear": average}


def print_report(fleet: list[dict]) -> None:
    """Print the nightly fleet-health summary and flush the log."""
    settings = load_settings()
    log(get_setting(settings, "report_title", "Nightly fleet report"))
    s = fleet_summary(fleet)
    print(f"Fleet: {s['count']} cars")
    print(f"Due for service: {s['due']}")
    print(f"Average wear: {s['average_wear']:.1f}%")
    total_km = 0
    for car in fleet:
        total_km = total_km + car["odometer"]
    # The partner garage in England reports in miles (since 2015).
    distance_miles = fleet_utils.km_to_miles(total_km)
    print(f"Fleet distance: {fleet_utils.format_number(distance_miles)} miles")
    flush_log(get_setting(settings, "log_file", "km_wachter.log"))