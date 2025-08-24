from typing import List
from app.core.strategies.base import JourneyBuilderStrategy
from app.dtos.flight_event_dto import FlightEventDTO
from app.dtos.flight_filter_dto import FlightFilterDTO
from app.utils.flight_commons import is_within_max_duration_1_event
from app.utils.config_vars import ConfigVars


class JourneyDirectFlights(JourneyBuilderStrategy):
    async def execute(
        self, flight_events: List[FlightEventDTO], flight_filter: FlightFilterDTO
    ) -> List[dict]:
        return [
            {"connections": 0, "path": [f]}
            for f in flight_events
            if f.departure_city == flight_filter.origin
            and f.arrival_city == flight_filter.destination
            and f.departure_date == flight_filter.date_only
            and await is_within_max_duration_1_event(f, ConfigVars.MAX_JOURNEY_HOURS)
        ]
