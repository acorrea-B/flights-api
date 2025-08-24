from datetime import datetime


class FlightEventDTO:
    def __init__(
        self,
        flight_number: str,
        departure_city: str,
        arrival_city: str,
        departure_datetime: datetime,
        arrival_datetime: datetime,
    ):
        self.flight_number = flight_number
        self.departure_city = departure_city
        self.arrival_city = arrival_city
        self.departure_datetime = departure_datetime
        self.arrival_datetime = arrival_datetime

    @property
    def departure_date(self):
        return self.departure_datetime.date()

    @property
    def arrival_date(self):
        return self.arrival_datetime.date()

    @classmethod
    def from_dict(cls, data: dict) -> "FlightEventDTO":
        return cls(
            flight_number=data.get("flight_number"),
            departure_city=data.get("departure_city"),
            arrival_city=data.get("arrival_city"),
            departure_datetime=datetime.fromisoformat(
                data.get("departure_datetime").replace("Z", "+00:00")
            ),
            arrival_datetime=datetime.fromisoformat(
                data.get("arrival_datetime").replace("Z", "+00:00")
            ),
        )
