from typing import List
from app.core.strategies.base import JourneyBuilderStrategy
from app.dtos.fligth_event_dto import FlightEventDTO
from app.dtos.flight_filter_dto import FlightFilterDTO


class JourneyDirectFlights(JourneyBuilderStrategy):
    async def execute(
        self, flight_events: List[FlightEventDTO], flight_filter: FlightFilterDTO
    ) -> List[List[FlightEventDTO]]:
        return [
            [f]
            for f in flight_events
            if f.departure_city == flight_filter.origin
            and f.arrival_city == flight_filter.destination
            and f.departure_date == flight_filter.date_only
        ]
