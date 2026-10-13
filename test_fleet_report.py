# test_fleet_report.py
import pytest

from fleet_report import fleet_summary

SAMPLE = [
    {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
    {"id": "VOS-2210", "odometer": 48400, "last_service_km": 45000},
]


def test_summary_counts_due_cars():
    # Only VOS-4471 is nearly worn, so exactly one car is due.
    assert fleet_summary(SAMPLE)["due"] == 1


# A car with no last_service_km reading (like VOS-7788 in fleet_sample.json) must not crash
# the report, and must not drag the fleet average towards zero as if it were freshly serviced.
UNREADABLE = {"id": "VOS-7788", "odometer": 92000}


def test_summary_survives_a_car_with_no_reading():
    fleet = SAMPLE + [UNREADABLE]
    summary = fleet_summary(fleet)

    assert summary["count"] == 3          # the unreadable car is still part of the fleet
    assert summary["due"] == 1            # ...but it is not falsely flagged as due
    assert summary["average_wear"] == pytest.approx(61.0)   # averaged over the 2 readable cars
