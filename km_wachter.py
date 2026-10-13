# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Written in 2013. Nobody has cleaned it up since.

from pathlib import Path

from config_loader import get_int, load_settings

# Built-in fallbacks. settings.cfg is the authoritative source for both rules -- these only
# apply when the config is missing or unreadable, and any disagreement between the two is
# reported at import rather than silently resolved in either direction.
SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80

SETTINGS_PATH = Path(__file__).parent / "settings.cfg"


def _rules_from_config() -> tuple[int, int]:
    """Return (service interval, warn percent) from settings.cfg, falling back to the built-ins."""
    try:
        settings = load_settings(SETTINGS_PATH)
    except OSError:
        return SERVICE_INTERVAL_KM, WARN_AT_PERCENT

    interval = get_int(settings, "service_interval_km", SERVICE_INTERVAL_KM)
    warn = get_int(settings, "warn_at_percent", WARN_AT_PERCENT)
    if (interval, warn) != (SERVICE_INTERVAL_KM, WARN_AT_PERCENT):
        print(f"WARNING: settings.cfg says interval={interval}, warn={warn}%, but the built-in "
              f"defaults are {SERVICE_INTERVAL_KM} and {WARN_AT_PERCENT}%. settings.cfg wins -- "
              "update the code so they agree.")
    return interval, warn


SERVICE_INTERVAL_KM, WARN_AT_PERCENT = _rules_from_config()


def wear_percent(km_since_service: float, interval: float) -> float:
    """Return how much of a service interval has been used up, as a percentage."""
    return km_since_service / interval * 100


def needs_service(car: dict) -> bool:
    """Return True if the car is at or past the warning threshold.

    A car with no last_service_km reading returns False. An unknown service
    history is never assumed to be either "freshly serviced" or "fully worn".
    """
    if "last_service_km" not in car:
        return False
    km_since = car["odometer"] - car["last_service_km"]
    return wear_percent(km_since, SERVICE_INTERVAL_KM) >= WARN_AT_PERCENT


def check_fleet(fleet: list[dict]) -> list[str]:
    """Return the ids of every car in the fleet that is due for service."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged