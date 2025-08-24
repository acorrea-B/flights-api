from typing import List
from app.core.strategies.base import JourneyBuilderStrategy
from app.dtos.flight_event_dto import FlightEventDTO
from app.dtos.flight_filter_dto import FlightFilterDTO
from app.utils.config_vars import ConfigVars
from app.utils.flight_commons import is_within_max_duration


class OneStopJourneyStrategy(JourneyBuilderStrategy):

    async def execute(
        self, flight_events: List[FlightEventDTO], flight_filter: FlightFilterDTO
    ) -> List[List[FlightEventDTO]]:
        connections = []
        for first_leg in flight_events:

            second_leg_list = await self.find_next_stopovers(
                first_leg, flight_events, flight_filter.destination
            )

            if second_leg_list:
                for second_leg in second_leg_list:
                    journey = [first_leg, second_leg]
                    if await is_within_max_duration(
                        journey, ConfigVars.MAX_JOURNEY_HOURS
                    ):
                        connections.append(
                            {"connections": len(journey) - 1, "path": journey}
                        )
        return connections

    async def find_next_stopovers(
        self,
        first_leg: FlightEventDTO,
        flight_events: list[FlightEventDTO],
        destination: str,
    ) -> List[FlightEventDTO]:
        valid_connections = []
        for next_stop in flight_events:
            if (
                next_stop.departure_city == first_leg.arrival_city
                and next_stop.arrival_city == destination
                and next_stop.departure_datetime > first_leg.arrival_datetime
            ):
                layover_duration = (
                    next_stop.departure_datetime - first_leg.arrival_datetime
                ).total_seconds() / 3600

                if 0 < layover_duration <= ConfigVars.MAX_LAYOVER_HOURS:
                    valid_connections.append(next_stop)
        return valid_connections
