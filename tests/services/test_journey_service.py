import unittest
from unittest.mock import patch, AsyncMock
from datetime import datetime
from app.services.journey_service import JourneyService
from app.dtos.flight_filter_dto import FlightFilterDTO
from app.dtos.flight_event_dto import FlightEventDTO
from tests.commons.test_helper import vcr


def create_flight_event_dict(
    flight_number="F1",
    departure_city="BUE",
    arrival_city="MAD",
    departure_datetime="2024-09-13T07:00:00Z",
    arrival_datetime="2024-09-13T13:00:00Z",
):
    return {
        "flight_number": flight_number,
        "departure_city": departure_city,
        "arrival_city": arrival_city,
        "departure_datetime": departure_datetime,
        "arrival_datetime": arrival_datetime,
    }


class TestJourneyService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.service = JourneyService()
        self.filter = FlightFilterDTO(
            date=datetime(2024, 9, 13), origin="BUE", destination="MAD"
        )

    def generate_flight_event_json(self):
        """
            Generates a list of flight event dicts for testing with 12 items.
            - There are 4 direct flights and 4 one-stop journeys possible.
            - There are 3 events that total is 2 journeys that exceed the max duration of 24.
              hours and should be filtered out betwen one-stop and direct flights.
            - There are 3 events on different dates that should be filtered out or layover is greather than 4.
            - There are 2 events that total is 2 journeys direct flights that match the filter and conditions.
            - There are 4 events that total is 2 journeys events one-stop that match the filter and conditions.
            para  criterio de filtro date=datetime(2024, 9, 13), origin="BUE", destination="MAD"
        """
        return [
            create_flight_event_dict(
                flight_number="AR1000",
                departure_datetime=str(datetime(2024, 9, 12, 7, 0).isoformat()),
                arrival_datetime=str(datetime(2024, 9, 12, 15, 0).isoformat()),
            ),
            create_flight_event_dict(
                flight_number="AR1001",
                departure_datetime=str(datetime(2024, 9, 13, 10, 0).isoformat()),
                arrival_datetime=str(datetime(2024, 9, 13, 18, 0).isoformat()),
            ),
            create_flight_event_dict(
                flight_number="AR1002",
                departure_datetime=str(datetime(2024, 9, 13, 5, 0).isoformat()),
                arrival_datetime=str(datetime(2024, 9, 13, 13, 0).isoformat()),
            ),
            create_flight_event_dict(
                flight_number="AR1003",
                departure_datetime=str(datetime(2024, 9, 13, 14, 0).isoformat()),
                arrival_datetime=str(
                    datetime(2024, 9, 14, 22, 0).isoformat()
                ),  # More than 24 hours
            ),
            create_flight_event_dict(
                "LA2000",
                "BUE",
                "GRU",
                str(datetime(2024, 9, 12, 6, 0).isoformat()),
                str(datetime(2024, 9, 12, 9, 0).isoformat()),
            ),
            create_flight_event_dict(
                "LA2000",
                "GRU",
                "MAD",
                str(datetime(2024, 9, 12, 14, 0).isoformat()),  # 4 hours layover
                str(datetime(2024, 9, 12, 19, 0).isoformat()),
            ),
            create_flight_event_dict(
                "AA3000",
                "BUE",
                "JFK",
                str(datetime(2024, 9, 13, 8, 0).isoformat()),
                str(datetime(2024, 9, 13, 16, 0).isoformat()),
            ),
            create_flight_event_dict(
                "AA3100",
                "JFK",
                "MAD",
                str(datetime(2024, 9, 13, 18, 0).isoformat()),
                str(datetime(2024, 9, 14, 2, 0).isoformat()),  # 18 flight hours
            ),
            create_flight_event_dict(
                "LA4000",
                "BUE",
                "SCL",
                str(datetime(2024, 9, 13, 9, 0).isoformat()),
                str(datetime(2024, 9, 13, 11, 30).isoformat()),
            ),
            create_flight_event_dict(
                "LA4100",
                "SCL",
                "MAD",
                str(datetime(2024, 9, 13, 13, 0).isoformat()),
                str(datetime(2024, 9, 14, 21, 30).isoformat()),  # more than 24 hours
            ),
            create_flight_event_dict(
                "LA5000",
                "BUE",
                "ATL",
                str(datetime(2024, 9, 13, 5, 0).isoformat()),
                str(datetime(2024, 9, 13, 7, 30).isoformat()),
            ),
            create_flight_event_dict(
                "LA5100",
                "ATL",
                "MAD",
                str(datetime(2024, 9, 13, 9, 0).isoformat()),
                str(datetime(2024, 9, 13, 17, 40).isoformat()),
            ),
        ]

    @vcr.use_cassette
    async def test_get_flight_events_with_data(self):
        flights = await self.service.get_flight_events()
        self.assertTrue(len(flights) > 0)
        self.assertIsInstance(flights[0], FlightEventDTO)
        self.assertEqual(flights[0].departure_city, "MAD")

    @patch(
        "app.adapters.flight_event_adapter.FlightEventAdapter.fetch_flight_events",
        new_callable=AsyncMock,
    )
    async def test_get_flight_events_raises_exception_when_empty(self, mock_fetch):
        mock_fetch.return_value = []
        with self.assertRaises(Exception) as context:
            await self.service.get_flight_events()
        self.assertIn("no flight events", str(context.exception).lower())

    @patch(
        "app.adapters.flight_event_adapter.FlightEventAdapter.fetch_flight_events",
        new_callable=AsyncMock,
    )
    async def test_build_journeys_calls_strategies_and_combines_results(
        self, mock_fetch
    ):
        mock_fetch.return_value = self.generate_flight_event_json()

        journeys = await self.service.build_journeys(self.filter)

        self.assertEqual(len(journeys), 4)  # 2 direct + 2 one-stop
        self.assertTrue(all(isinstance(j, dict) for j in journeys))
        self.assertTrue(all("connections" in j and "path" in j for j in journeys))
        
        journeys_with_0_connections = [j for j in journeys if j["connections"] == 0]
        journeys_with_1_connection = [j for j in journeys if j["connections"] == 1]
        self.assertEqual(len(journeys_with_0_connections), 2)
        self.assertEqual(len(journeys_with_1_connection), 2)

        self.assertTrue(all(len(j["path"]) == 1 for j in journeys_with_0_connections))
        self.assertTrue(all(len(j["path"]) == 2 for j in journeys_with_1_connection))

        self.assertTrue(all(j["path"][0].departure_city == "BUE" for j in journeys))
        self.assertTrue(all(j["path"][-1].arrival_city == "MAD" for j in journeys))
        mock_fetch.assert_awaited_once()

    @patch("app.services.journey_service.report_error")
    @patch(
        "app.adapters.flight_event_adapter.FlightEventAdapter.fetch_flight_events",
        new_callable=AsyncMock,
    )
    @patch(
        "app.core.strategies.direct_flights.JourneyDirectFlights.execute",
        new_callable=AsyncMock,
    )
    @patch(
        "app.core.strategies.one_stop.OneStopJourneyStrategy.execute",
        new_callable=AsyncMock,
    )
    async def test_build_journeys_when_strategies_return_empty(
        self, mock_one_stop, mock_direct, mock_fetch, mock_report_error
    ):
        mock_fetch.return_value = []


        journeys = await self.service.build_journeys(self.filter)

        self.assertEqual(journeys, [])

        mock_report_error.assert_called_with(
            f"There are no flight events available at the moment. : {self.filter.__dict__}"
        )
        mock_direct.assert_not_awaited()
        mock_one_stop.assert_not_awaited()
        mock_fetch.assert_awaited_once()
