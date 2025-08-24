from fastapi import APIRouter, Depends
from typing import List

from fastapi import Query
from datetime import date
from app.api.v1.responses.journey_response import JourneyResponse
from app.services.journey_service import JourneyService
from app.dtos.flight_filter_dto import FlightFilterDTO

router = APIRouter(prefix="/journeys", tags=["journeys"])


@router.get("/search", response_model=List[JourneyResponse])
async def search_flights(
    date: date,
    origin: str = Query(
        ..., alias="from", min_length=3, max_length=3, pattern=r"^[A-Z]+$"
    ),
    destination: str = Query(
        ..., alias="to", min_length=3, max_length=3, pattern=r"^[A-Z]+$"
    ),
):
    filter_dto = FlightFilterDTO(date, origin, destination)
    raw_results = await JourneyService().build_journeys(filter_dto)

    return list(map(JourneyResponse.from_dto, raw_results))
