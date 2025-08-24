from datetime import date


class FlightFilterDTO:
    def __init__(self, date: date, origin: str, destination: str):
        self.date = date
        self.origin = origin
        self.destination = destination
