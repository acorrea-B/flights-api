import unittest
from datetime import datetime, timedelta
from app.utils.flight_commons import (
    is_within_max_duration,
    is_within_max_duration_1_event,
    validate_time,
)
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

    async def test_is_within_max_duration_1_event_valid(self):
        dep = datetime(2024, 9, 12, 12, 0)
        arr = dep + timedelta(hours=3)
        event = create_event(dep, arr)
        result = await is_within_max_duration_1_event(event, max_hours_travel=4)
        self.assertTrue(result)

    async def test_is_within_max_duration_1_event_exceeds(self):
        dep = datetime(2024, 9, 12, 10, 0)
        arr = dep + timedelta(hours=7)
        event = create_event(dep, arr)
        result = await is_within_max_duration_1_event(event, max_hours_travel=6)
        self.assertFalse(result)

    async def test_is_within_max_duration_1_event_none(self):
        result = await is_within_max_duration_1_event(None, max_hours_travel=5)
        self.assertFalse(result)

    async def test_validate_time_within_limit(self):
        dep = datetime(2024, 9, 12, 10, 0)
        arr = dep + timedelta(hours=3)
        result = await validate_time(arrival=arr, departure=dep, max_hours_travel=4)
        self.assertTrue(result)

    async def test_validate_time_exact_limit(self):
        dep = datetime(2024, 9, 12, 10, 0)
        arr = dep + timedelta(hours=5)
        result = await validate_time(arrival=arr, departure=dep, max_hours_travel=5)
        self.assertTrue(result)

    async def test_validate_time_exceeds_limit(self):
        dep = datetime(2024, 9, 12, 10, 0)
        arr = dep + timedelta(hours=6)
        result = await validate_time(arrival=arr, departure=dep, max_hours_travel=5)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
