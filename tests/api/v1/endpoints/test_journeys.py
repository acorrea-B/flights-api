import unittest
from fastapi.testclient import TestClient
from tests.commons.factorie import generate_flight_event_json
from unittest.mock import patch, AsyncMock
from tests.commons.test_helper import vcr

from main import app


class TestJourneySearchAPI(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.base_url = "/v1/journeys/search"

    @vcr.use_cassette
    def test_valid_request_should_return_results(self):
        response = self.client.get(
            self.base_url, params={"date": "2021-12-31", "from": "MAD", "to": "BUE"}
        )
        results = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIn("connections", results[0])
        self.assertIn("path", results[0])

        self.assertEqual(results[0]["connections"], 0)
        path = results[0]["path"][0]
        self.assertEqual(path["flight_number"], "IB1234")
        self.assertEqual(path["from"], "MAD")
        self.assertEqual(path["to"], "BUE")
        self.assertEqual(path["departure_time"], "2021-12-31 23:59")
        self.assertEqual(path["arrival_time"], "2022-01-01 12:00")

    def test_valid_request_should_not_return_results(self):
        response = self.client.get(
            self.base_url, params={"date": "2021-12-01", "from": "MAD", "to": "BUE"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 0)

    @patch(
        "app.adapters.flight_event_adapter.FlightEventAdapter.fetch_flight_events",
        new_callable=AsyncMock,
    )
    async def test_valid_request_should_return_results_with_mock_data(self, mock_fetch):
        mock_fetch.return_value = generate_flight_event_json()

        response = self.client.get(
            self.base_url, params={"date": "2024-09-13", "from": "BUE", "to": "MAD"}
        )
        results = response.json()
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(results), 4)  # 2 direct + 2 one-stop
        self.assertTrue(all(isinstance(j, dict) for j in results))
        self.assertTrue(all("connections" in j and "path" in j for j in results))

        journeys_with_0_connections = [j for j in results if j["connections"] == 0]
        journeys_with_1_connection = [j for j in results if j["connections"] == 1]
        self.assertEqual(len(journeys_with_0_connections), 2)
        self.assertEqual(len(journeys_with_1_connection), 2)

        self.assertTrue(all(len(j["path"]) == 1 for j in journeys_with_0_connections))
        self.assertTrue(all(len(j["path"]) == 2 for j in journeys_with_1_connection))

        self.assertTrue(all(j["path"][0]["from"] == "BUE" for j in results))
        self.assertTrue(all(j["path"][-1]["to"] == "MAD" for j in results))
        mock_fetch.assert_awaited_once()

    def test_invalid_date_format_should_fail(self):
        response = self.client.get(
            self.base_url,
            params={
                "date": "13-09-2024",  # incorrect format
                "from": "BUE",
                "to": "MAD",
            },
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())

    def test_invalid_origin_code_too_short(self):
        response = self.client.get(
            self.base_url,
            params={"date": "2024-09-13", "from": "BU", "to": "MAD"},  # too short
        )
        self.assertEqual(response.status_code, 422)

    def test_invalid_origin_code_lowercase(self):
        response = self.client.get(
            self.base_url,
        )
        self.assertEqual(response.status_code, 422)

    def test_missing_params_should_fail(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 422)
