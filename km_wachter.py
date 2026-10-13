# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Written in 2013. Nobody has cleaned it up since.

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service, interval):
    return km_since_service / interval * 100


def needs_service(car):
    if "last_service_km" not in car:
        return False                        # no reading: never assume it was zero
    km_since = car["odometer"] - car["last_service_km"]
    pct = wear_percent(km_since, SERVICE_INTERVAL_KM)
    if pct >= WARN_AT_PERCENT:
        return True
    else:
        return False


def check_fleet(fleet):
    flagged = []
    for car in fleet:
        if needs_service(car) == True:
            flagged.append(car["id"])
            print("SERVICE DUE: %s" % car["id"])
    return flagged
