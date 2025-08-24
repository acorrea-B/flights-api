import unittest
from unittest.mock import patch, AsyncMock
from datetime import datetime
from app.services.journey_service import JourneyService
from app.dtos.flight_filter_dto import FlightFilterDTO
from app.dtos.flight_event_dto import FlightEventDTO
from tests.commons.test_helper import vcr
from tests.commons.factorie import generate_flight_event_json




class TestJourneyService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.service = JourneyService()
        self.filter = FlightFilterDTO(
            date=datetime(2024, 9, 13).date(), origin="BUE", destination="MAD"
        )


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
        mock_fetch.return_value = generate_flight_event_json()

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
