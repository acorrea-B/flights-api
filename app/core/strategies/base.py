from abc import ABC, abstractmethod
from typing import List
from app.dtos.flight_event_dto import FlightEventDTO
from app.dtos.flight_filter_dto import FlightFilterDTO


class JourneyBuilderStrategy(ABC):
    @abstractmethod
    async def execute(
        self, flight_events: List[FlightEventDTO], flight_filter: FlightFilterDTO
    ) -> List[dict]:
        pass

