from typing import List
from datetime import datetime
from app.dtos.fligth_event_dto import FlightEventDTO


async def validate_time(
    arrival: datetime, departure: datetime, max_hours_travel: int
) -> bool:
    total_duration = (arrival - departure).total_seconds() / 3600

    return total_duration <= max_hours_travel


async def is_within_max_duration_1_event(
    event: FlightEventDTO, max_hours_travel: int
) -> bool:
    if not event:
        return False
    departure = event.departure_datetime
    arrival = event.arrival_datetime

    return await validate_time(arrival, departure, max_hours_travel)


async def is_within_max_duration(
    events: List[FlightEventDTO], max_hours_travel: int
) -> bool:
    if not events:
        return False
    departure = events[0].departure_datetime
    arrival = events[-1].arrival_datetime

    return await validate_time(arrival, departure, max_hours_travel)
