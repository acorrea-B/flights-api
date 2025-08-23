import unittest
from unittest.mock import patch, AsyncMock
from datetime import datetime
from app.services.journey_service import JourneyService
from app.dtos.flight_filter_dto import FlightFilterDTO
from app.dtos.fligth_event_dto import FlightEventDTO
from tests.commons.test_helper import vcr

def create_flight_event_dict(
    flight_number="F1",
    departure_city="BUE",
    arrival_city="MAD",
    departure_datetime="2024-09-12T07:00:00Z",
    arrival_datetime="2024-09-12T13:00:00Z"
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
            date=datetime(2024, 9, 12),
            origin="BUE",
            destination="PMI"
        )

    @vcr.use_cassette
    async def test_get_flight_events_with_data(self):
        flights = await self.service.get_flight_events()
        self.assertTrue(len(flights) > 0)
        self.assertIsInstance(flights[0], FlightEventDTO)
        self.assertEqual(flights[0].departure_city, "BUE")

    @patch("app.adapters.flight_event_adapter.FlightEventAdapter.fetch_flight_events", new_callable=AsyncMock)
    async def test_get_flight_events_raises_exception_when_empty(self, mock_fetch):
        mock_fetch.return_value = []
        with self.assertRaises(Exception) as context:
            await self.service.get_flight_events()
        self.assertIn("no flight events", str(context.exception).lower())

    @patch("app.adapters.flight_event_adapter.FlightEventAdapter.fetch_flight_events", new_callable=AsyncMock)
    @patch("app.core.strategies.direct_flights.JourneyDirectFlights.execute", new_callable=AsyncMock)
    @patch("app.core.strategies.one_stop.OneStopJourneyStrategy.execute", new_callable=AsyncMock)
    async def test_build_journeys_calls_strategies_and_combines_results(
        self, mock_one_stop, mock_direct, mock_fetch
    ):
        # Mock fetch devuelve lista con un dict vuelo
        mock_fetch.return_value = [
            create_flight_event_dict()
        ]

        # Crear un mock de FlightEventDTO para las estrategias
        mock_flight_event = FlightEventDTO.from_dict(create_flight_event_dict())

        # Mock de estrategias que retornen listas de listas (listas de viajes)
        mock_direct.return_value = [[mock_flight_event]]
        mock_one_stop.return_value = [[mock_flight_event, mock_flight_event]]

        journeys = await self.service.build_journeys(self.filter)

        # Validar que el resultado es combinación de ambas estrategias
        self.assertEqual(len(journeys), 2)
        self.assertIn([mock_flight_event], journeys)
        self.assertIn([mock_flight_event, mock_flight_event], journeys)

        # Validar que las estrategias se llamaron con los argumentos correctos
        mock_direct.assert_awaited_once()
        mock_one_stop.assert_awaited_once()
        mock_fetch.assert_awaited_once()

    @patch("app.adapters.flight_event_adapter.FlightEventAdapter.fetch_flight_events", new_callable=AsyncMock)
    @patch("app.core.strategies.direct_flights.JourneyDirectFlights.execute", new_callable=AsyncMock)
    @patch("app.core.strategies.one_stop.OneStopJourneyStrategy.execute", new_callable=AsyncMock)
    async def test_build_journeys_when_strategies_return_empty(
        self, mock_one_stop, mock_direct, mock_fetch
    ):
        mock_fetch.return_value = [
            create_flight_event_dict()
        ]

        mock_direct.return_value = []
        mock_one_stop.return_value = []

        journeys = await self.service.build_journeys(self.filter)

        self.assertEqual(journeys, [])

        mock_direct.assert_awaited_once()
        mock_one_stop.assert_awaited_once()
        mock_fetch.assert_awaited_once()
