import unittest
from datetime import datetime, timedelta
from app.utils.flight_commons import is_within_max_duration
from app.dtos.flight_event_dto import FlightEventDTO


def create_event(departure, arrival) -> FlightEventDTO:
    return FlightEventDTO(
        flight_number="XX999",
        departure_city="AAA",
        arrival_city="BBB",
        departure_datetime=departure,
        arrival_datetime=arrival,
    )


class TestIsWithinMaxDuration(unittest.IsolatedAsyncioTestCase):
    async def test_single_event_within_duration(self):
        dep = datetime(2024, 9, 12, 10, 0)
        arr = dep + timedelta(hours=4)
        result = await is_within_max_duration(
            [create_event(dep, arr)], max_hours_travel=5
        )
        self.assertTrue(result)

    async def test_single_event_exceeds_duration(self):
        dep = datetime(2024, 9, 12, 10, 0)
        arr = dep + timedelta(hours=6)
        result = await is_within_max_duration(
            [create_event(dep, arr)], max_hours_travel=5
        )
        self.assertFalse(result)

    async def test_two_events_within_duration(self):
        dep1 = datetime(2024, 9, 12, 8, 0)
        arr1 = dep1 + timedelta(hours=2)

        dep2 = arr1 + timedelta(hours=1)
        arr2 = dep2 + timedelta(hours=2)

        result = await is_within_max_duration(
            [create_event(dep1, arr1), create_event(dep2, arr2)], max_hours_travel=6
        )
        self.assertTrue(result)

    async def test_two_events_exceed_duration(self):
        dep1 = datetime(2024, 9, 12, 8, 0)
        arr1 = dep1 + timedelta(hours=3)

        dep2 = arr1 + timedelta(hours=2)
        arr2 = dep2 + timedelta(hours=3)

        result = await is_within_max_duration(
            [create_event(dep1, arr1), create_event(dep2, arr2)], max_hours_travel=6
        )
        self.assertFalse(result)

    async def test_empty_event_list(self):
        result = await is_within_max_duration([], max_hours_travel=5)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
