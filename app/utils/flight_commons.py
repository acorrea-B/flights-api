from typing import List
from app.dtos.fligth_event_dto import FlightEventDTO


async def is_within_max_duration(events: List[FlightEventDTO], max_hours_travel: int) -> bool:
    if not events:
        return False
    departure = events[0].departure_datetime
    arrival = events[-1].arrival_datetime

    total_duration = (arrival - departure).total_seconds() / 3600

    return total_duration <= max_hours_travel
