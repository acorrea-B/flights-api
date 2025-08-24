import httpx

from typing import List, Dict, Any, Optional
from app.utils.config_vars import ConfigVars
from app.utils.logger import report_error
from app.utils.config_vars import ConfigVars

class FlightEventAdapter:
    def __init__(self):
        self.base_url = ConfigVars.FLIGHT_EVENTS_API_URL
        self.timeout = ConfigVars.DEFAULT_API_TIMEOUT


    async def fetch_flight_events(self) -> Optional[List[Dict[str, Any]]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url)
                response.raise_for_status()

                return response.json()

        except httpx.TimeoutException as exc:
            report_error(f"Timeout error while requesting flight events: {str(exc)}")
        except httpx.RequestError as exc:
            report_error(f"Connection error while requesting flight events: {str(exc)}")
        except httpx.HTTPStatusError as exc:
            report_error(
                f"HTTP {exc.response.status_code} error received from flight events API, {str(exc)}",
            )
        except Exception as exc:
            report_error(f"Unexpected error when fetching flight events: {str(exc)}")

        return None
