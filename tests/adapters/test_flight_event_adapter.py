import unittest
import asyncio
import httpx

from tests.commons.test_helper import vcr
from unittest.mock import patch, Mock
from app.adapters.flight_event_adapter import FlightEventAdapter


class TestFlightEventAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = FlightEventAdapter()
        self.adapter.timeout = 5
        self.loop = asyncio.get_event_loop()

    def get_expected_response(self):
        return [
            {
                "flight_number": "IB1234",
                "departure_city": "MAD",
                "arrival_city": "BUE",
                "departure_datetime": "2021-12-31T23:59:59.000Z",
                "arrival_datetime": "2022-01-01T12:00:00.000Z",
            }
        ]

    @vcr.use_cassette
    def test_fetch_flight_events_success(self):
        result = self.loop.run_until_complete(self.adapter.fetch_flight_events())
        self.assertIsInstance(result, list)
        self.assertEqual(result, self.get_expected_response())

    @patch("app.adapters.flight_event_adapter.report_error")
    @patch("app.adapters.flight_event_adapter.httpx.AsyncClient.get")
    def test_timeout_exception(self, mock_get, mock_report_error):
        mock_get.side_effect = httpx.TimeoutException("Request timed out")
        result = self.loop.run_until_complete(self.adapter.fetch_flight_events())
        self.assertIsNone(result)
        mock_report_error.assert_called_with(
            "Timeout error while requesting flight events: Request timed out"
        )

    @patch("app.adapters.flight_event_adapter.report_error")
    @patch("app.adapters.flight_event_adapter.httpx.AsyncClient")
    def test_request_error(self, mock_async_client_cls, mock_report_error):
        mock_client = mock_async_client_cls.return_value.__aenter__.return_value
        mock_client.get.side_effect = httpx.RequestError("Connection failed")

        result = self.loop.run_until_complete(self.adapter.fetch_flight_events())

        self.assertIsNone(result)
        mock_report_error.assert_called_with(
            "Connection error while requesting flight events: Connection failed"
        )

    @patch("app.adapters.flight_event_adapter.report_error")
    @patch("app.adapters.flight_event_adapter.httpx.AsyncClient")
    def test_http_status_error(self, mock_async_client_cls, mock_report_error):
        mock_client = mock_async_client_cls.return_value.__aenter__.return_value
        response_mock = Mock()
        response_mock.status_code = 500
        mock_client.get.side_effect = httpx.HTTPStatusError(
            "Internal Server Error", request=None, response=response_mock
        )

        result = self.loop.run_until_complete(self.adapter.fetch_flight_events())

        self.assertIsNone(result)
        mock_report_error.assert_called_with(
            "HTTP 500 error received from flight events API, Internal Server Error"
        )

    @patch("app.adapters.flight_event_adapter.report_error")
    @patch("app.adapters.flight_event_adapter.httpx.AsyncClient")
    def test_unexpected_exception(self, mock_async_client_cls, mock_report_error):
        mock_client = mock_async_client_cls.return_value.__aenter__.return_value
        mock_client.get.side_effect = Exception("Something went wrong")

        result = self.loop.run_until_complete(self.adapter.fetch_flight_events())

        self.assertIsNone(result)
        mock_report_error.assert_called_with(
            "Unexpected error when fetching flight events: Something went wrong"
        )


if __name__ == "__main__":
    unittest.main()
