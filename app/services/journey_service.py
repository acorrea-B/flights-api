from typing import List
from app.core.strategies.direct_flights import JourneyDirectFlights
from app.core.strategies.one_stop import OneStopJourneyStrategy
from app.adapters.flight_event_adapter import FlightEventAdapter
from app.dtos.fligth_event_dto import FlightEventDTO
from app.dtos.flight_filter_dto import FlightFilterDTO


class JourneyService:
    def __init__(self):
        self.adapter = FlightEventAdapter()
        self.strategies = [
            JourneyDirectFlights(),
            OneStopJourneyStrategy(),
        ]

    async def get_flight_events(self) -> list[FlightEventDTO]:
        raw_events = await self.adapter.fetch_flight_events()
        if not raw_events:
            raise Exception("There are no flight events available at the moment.")
        return list(map(FlightEventDTO.from_dict, raw_events))

    async def build_journeys(
        self, flight_filter: FlightFilterDTO
    ) -> List[List[FlightEventDTO]]:
        flight_events = await self.get_flight_events()
        journeys = []
        for strategy in self.strategies:
            result = await strategy.execute(flight_events, flight_filter)
            journeys.extend(result)
        return journeys
