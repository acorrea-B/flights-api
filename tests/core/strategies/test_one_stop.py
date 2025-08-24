import unittest
from datetime import datetime

from app.core.strategies.one_stop import OneStopJourneyStrategy
from app.dtos.flight_event_dto import FlightEventDTO
from app.dtos.flight_filter_dto import FlightFilterDTO


def create_event(
    flight_number: str,
    departure_city: str,
    arrival_city: str,
    departure_dt: datetime,
    arrival_dt: datetime,
) -> FlightEventDTO:
    return FlightEventDTO(
        flight_number=flight_number,
        departure_city=departure_city,
        arrival_city=arrival_city,
        departure_datetime=departure_dt,
        arrival_datetime=arrival_dt,
    )


class TestOneStopJourneyStrategy(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.strategy = OneStopJourneyStrategy()
        self.filter = FlightFilterDTO(
            date=datetime(2024, 9, 12).date(),
            origin="BUE",
            destination="PMI",
        )
        self.first_leg = FlightEventDTO(
            flight_number="F1",
            departure_city="BUE",
            arrival_city="MAD",
            departure_datetime=datetime(2024, 9, 12, 7, 0),
            arrival_datetime=datetime(2024, 9, 12, 13, 0),
        )

    async def test_valid_one_stop_journey(self):
        flight1 = create_event(
            "XX1234",
            "BUE",
            "MAD",
            datetime(2024, 9, 12, 10, 0),
            datetime(2024, 9, 12, 18, 0),
        )
        flight2 = create_event(
            "XX2345",
            "MAD",
            "PMI",
            datetime(2024, 9, 12, 19, 0),
            datetime(2024, 9, 12, 20, 0),
        )

        journeys = await self.strategy.execute([flight1, flight2], self.filter)
        self.assertEqual(len(journeys), 1)
        self.assertEqual(journeys[0]["connections"], 1)
        self.assertEqual(len(journeys[0]["path"]), 2)
        self.assertEqual(journeys[0]["path"][0].flight_number, "XX1234")
        self.assertEqual(journeys[0]["path"][1].flight_number, "XX2345")

    async def test_invalid_due_to_long_layover(self):
        flight1 = create_event(
            "XX1234",
            "BUE",
            "MAD",
            datetime(2024, 9, 12, 10, 0),
            datetime(2024, 9, 12, 12, 0),
        )
        flight2 = create_event(
            "XX2345",
            "MAD",
            "PMI",
            datetime(2024, 9, 12, 17, 0),  # 5h layover
            datetime(2024, 9, 12, 18, 0),
        )

        journeys = await self.strategy.execute([flight1, flight2], self.filter)
        self.assertEqual(journeys, [])

    async def test_invalid_due_to_total_duration(self):
        flight1 = create_event(
            "XX1234",
            "BUE",
            "MAD",
            datetime(2024, 9, 12, 1, 0),
            datetime(2024, 9, 12, 5, 0),
        )
        flight2 = create_event(
            "XX2345",
            "MAD",
            "PMI",
            datetime(2024, 9, 12, 6, 0),
            datetime(2024, 9, 13, 5, 30),  # Total > 24h
        )

        journeys = await self.strategy.execute([flight1, flight2], self.filter)
        self.assertEqual(journeys, [])

    async def test_missing_connection(self):
        flight1 = create_event(
            "XX1234",
            "BUE",
            "MAD",
            datetime(2024, 9, 12, 10, 0),
            datetime(2024, 9, 12, 18, 0),
        )
        # No flight MAD → PMI
        flight2 = create_event(
            "XX2345",
            "MAD",
            "BCN",
            datetime(2024, 9, 12, 19, 0),
            datetime(2024, 9, 12, 20, 0),
        )

        journeys = await self.strategy.execute([flight1, flight2], self.filter)
        self.assertEqual(journeys, [])

    async def test_multiple_valid_journeys(self):
        flight1 = create_event(
            "F1",
            "BUE",
            "MAD",
            datetime(2024, 9, 12, 7, 0),
            datetime(2024, 9, 12, 13, 0),
        )
        flight2 = create_event(
            "F2",
            "MAD",
            "PMI",
            datetime(2024, 9, 12, 14, 0),
            datetime(2024, 9, 12, 15, 0),
        )
        flight3 = create_event(
            "F3",
            "MAD",
            "PMI",
            datetime(2024, 9, 12, 15, 30),
            datetime(2024, 9, 12, 16, 30),
        )

        journeys = await self.strategy.execute([flight1, flight2, flight3], self.filter)
        self.assertEqual(len(journeys), 2)

    async def test_no_flights_returns_empty(self):
        result = await self.strategy.find_next_stopovers(self.first_leg, [], "PMI")
        self.assertEqual(result, [])

    async def test_valid_flight_is_included(self):
        valid_leg = FlightEventDTO(
            flight_number="F2",
            departure_city="MAD",
            arrival_city="PMI",
            departure_datetime=datetime(2024, 9, 12, 14, 0),
            arrival_datetime=datetime(2024, 9, 12, 15, 0),
        )
        result = await self.strategy.find_next_stopovers(
            self.first_leg, [valid_leg], "PMI"
        )
        self.assertIn(valid_leg, result)

    async def test_departure_city_must_match_first_leg_arrival(self):
        wrong_departure = FlightEventDTO(
            flight_number="F3",
            departure_city="BCN",
            arrival_city="PMI",
            departure_datetime=datetime(2024, 9, 12, 14, 0),
            arrival_datetime=datetime(2024, 9, 12, 15, 0),
        )
        result = await self.strategy.find_next_stopovers(
            self.first_leg, [wrong_departure], "PMI"
        )
        self.assertNotIn(wrong_departure, result)

    async def test_arrival_city_must_match_destination(self):
        wrong_arrival = FlightEventDTO(
            flight_number="F4",
            departure_city="MAD",
            arrival_city="BCN",  # does not match PMI
            departure_datetime=datetime(2024, 9, 12, 14, 0),
            arrival_datetime=datetime(2024, 9, 12, 15, 0),
        )
        result = await self.strategy.find_next_stopovers(
            self.first_leg, [wrong_arrival], "PMI"
        )
        self.assertNotIn(wrong_arrival, result)

    async def test_departure_after_arrival(self):
        early_departure = FlightEventDTO(
            flight_number="F5",
            departure_city="MAD",
            arrival_city="PMI",
            departure_datetime=datetime(2024, 9, 12, 12, 0),
            arrival_datetime=datetime(2024, 9, 12, 13, 0),
        )
        result = await self.strategy.find_next_stopovers(
            self.first_leg, [early_departure], "PMI"
        )
        self.assertNotIn(early_departure, result)

    async def test_layover_must_be_positive_and_within_max(self):
        zero_layover = FlightEventDTO(
            flight_number="F6",
            departure_city="MAD",
            arrival_city="PMI",
            departure_datetime=self.first_leg.arrival_datetime,
            arrival_datetime=datetime(2024, 9, 12, 15, 0),
        )
        long_layover = FlightEventDTO(
            flight_number="F7",
            departure_city="MAD",
            arrival_city="PMI",
            departure_datetime=self.first_leg.arrival_datetime.replace(hour=23),
            arrival_datetime=datetime(2024, 9, 13, 1, 0),
        )
        result = await self.strategy.find_next_stopovers(
            self.first_leg, [zero_layover, long_layover], "PMI"
        )
        self.assertNotIn(zero_layover, result)
        self.assertNotIn(long_layover, result)

    async def test_multiple_valid_stopovers(self):
        valid1 = FlightEventDTO(
            flight_number="F8",
            departure_city="MAD",
            arrival_city="PMI",
            departure_datetime=self.first_leg.arrival_datetime.replace(hour=14),
            arrival_datetime=datetime(2024, 9, 12, 15, 0),
        )
        valid2 = FlightEventDTO(
            flight_number="F9",
            departure_city="MAD",
            arrival_city="PMI",
            departure_datetime=self.first_leg.arrival_datetime.replace(hour=15),
            arrival_datetime=datetime(2024, 9, 12, 16, 0),
        )
        result = await self.strategy.find_next_stopovers(
            self.first_leg, [valid1, valid2], "PMI"
        )
        self.assertIn(valid1, result)
        self.assertIn(valid2, result)
        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
