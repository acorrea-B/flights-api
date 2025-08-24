from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from datetime import date as input_date
from app.dtos.flight_filter_dto import FlightFilterDTO


class FlightSearchRequest(BaseModel):
    date: input_date = Field(..., description="Date in format YYYY-MM-DD")
    from_:str= Field(..., alias='from')
    to: Annotated[
        str, Field(..., description="Destination airport code (3 uppercase letters)")
    ]

    model_config = ConfigDict(populate_by_name=True)

    def to_dto(self) -> FlightFilterDTO:
        return FlightFilterDTO(
            date=self.date,
            origin=self.from_,
            destination=self.to,
        )
