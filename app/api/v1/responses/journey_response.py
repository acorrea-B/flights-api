from pydantic import BaseModel, Field, ConfigDict
from typing import List
from app.dtos.flight_event_dto import FlightEventDTO


class FlightItem(BaseModel):
    flight_number: str
    from_: str = Field(..., alias='from')
    to: str
    departure_time: str
    arrival_time: str

    model_config = ConfigDict(populate_by_name=True)


    @classmethod
    def from_dto(cls, dto: FlightEventDTO) -> "FlightItem":
        return cls(
            flight_number=dto.flight_number,
            from_=dto.departure_city,
            to=dto.arrival_city,
            departure_time=dto.departure_datetime.strftime("%Y-%m-%d %H:%M"),
            arrival_time=dto.arrival_datetime.strftime("%Y-%m-%d %H:%M"),
        )


class JourneyResponse(BaseModel):
    connections: int
    path: List[FlightItem]

    @classmethod
    def from_dto(cls, journey) -> "JourneyResponse":
        return cls(
            connections=journey["connections"],
            path=list(map(FlightItem.from_dto, journey["path"])),
        )
