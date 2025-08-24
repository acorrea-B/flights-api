from datetime import datetime


class FlightFilterDTO:
    def __init__(self, date: datetime, origin: str, destination: str):
        self.date = date
        self.origin = origin
        self.destination = destination
    
    @property
    def date_only(self):
        return self.date.date()