import unittest
from datetime import datetime
from typing import List

from app.core.strategies.direct_flights import JourneyDirectFlights
from app.dtos.flight_event_dto import FlightEventDTO
from app.dtos.flight_filter_dto import FlightFilterDTO


def create_event(
    flight_number: str,
    departure_city: str,
    arrival_city: str,
    departure_datetime: datetime,
    arrival_datetime: datetime,
) -> FlightEventDTO:
    return FlightEventDTO(
        flight_number=flight_number,
        departure_city=departure_city,
        arrival_city=arrival_city,
        departure_datetime=departure_datetime,
        arrival_datetime=arrival_datetime,
    )


class TestJourneyDirectFlights(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.filter = FlightFilterDTO(
            date=datetime(2024, 9, 12).date(), origin="BUE", destination="MAD"
        )
        self.strategy = JourneyDirectFlights()

    async def test_one_direct_flight_match(self):

        flight = create_event(
            "XX1234",
            "BUE",
            "MAD",
            datetime(2024, 9, 12, 12, 0),
            datetime(2024, 9, 12, 22, 0),
        )

        result = await self.strategy.execute([flight], self.filter)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]["path"]), 1)
        self.assertEqual(result[0]["path"][0].flight_number, "XX1234")
        self.assertEqual(result[0]["connections"], 0)

    async def test_no_direct_flights_match(self):
        filter = FlightFilterDTO(
            date=datetime(2024, 9, 12), origin="BUE", destination="NYC"
        )

        flight = create_event(
            "XX1234",
            "BUE",
            "MAD",
            datetime(2024, 9, 12, 12, 0),
            datetime(2024, 9, 12, 22, 0),
        )

        result = await self.strategy.execute([flight], filter)
        self.assertEqual(result, [])

    async def test_flight_different_date(self):
        flight = create_event(
            "XX1234",
            "BUE",
            "MAD",
            datetime(2024, 9, 13, 12, 0),
            datetime(2024, 9, 13, 22, 0),
        )

        result = await self.strategy.execute([flight], self.filter)
        self.assertEqual(result, [])
    
    async def test_flight_more_than_24_hours(self):
        flight = create_event(
            "XX1234",
            "BUE",
            "MAD",
            datetime(2024, 9, 13, 12, 0),
            datetime(2024, 9, 14, 22, 0),
        )

        result = await self.strategy.execute([flight], self.filter)
        self.assertEqual(result, [])

    async def test_multiple_flights(self):

        flights: List[FlightEventDTO] = [
            create_event(
                "XX1111",
                "BUE",
                "MAD",
                datetime(2024, 9, 12, 8, 0),
                datetime(2024, 9, 12, 16, 0),
            ),
            create_event(
                "XX1111",
                "BUE",
                "MAD",
                datetime(2024, 9, 12, 8, 0),
                datetime(2024, 9, 13, 16, 0), # More than 24 hours
            ),
            create_event(
                "XX1111",
                "BUE",
                "MAD",
                datetime(2024, 9, 12, 8, 0),
                datetime(2024, 9, 13, 8, 0), # 24 hours
            ),
            create_event(
                "XX2222",
                "BUE",
                "NYC",
                datetime(2024, 9, 12, 9, 0),
                datetime(2024, 9, 12, 17, 0),
            ),
            create_event(
                "XX2222",
                "NYC",
                "MAD",
                datetime(2024, 9, 12, 9, 0),
                datetime(2024, 9, 12, 17, 0),
            ),
            create_event(
                "XX2222",
                "BUE",
                "ATL",
                datetime(2024, 9, 12, 9, 0),
                datetime(2024, 9, 12, 17, 0),
            ),
            create_event(
                "XX3333",
                "BUE",
                "MAD",
                datetime(2024, 9, 12, 12, 0),
                datetime(2024, 9, 12, 20, 0),
            ),
            create_event(
                "XX3333",
                "BUE",
                "MAD",
                datetime(2024, 9, 13, 12, 0),
                datetime(2024, 9, 13, 20, 0),
            ),
        ]

        result = await self.strategy.execute(flights, self.filter)
        self.assertEqual(len(result), 3)
        self.assertTrue(all(j["connections"] == 0 for j in result))
        self.assertTrue(all(len(j["path"]) == 1 for j in result))
        self.assertTrue(all(j["path"][0].arrival_city == "MAD" for j in result))


if __name__ == "__main__":
    unittest.main()
