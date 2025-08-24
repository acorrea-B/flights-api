from datetime import datetime


def create_flight_event_dict(
    flight_number="F1",
    departure_city="BUE",
    arrival_city="MAD",
    departure_datetime="2024-09-13T07:00:00Z",
    arrival_datetime="2024-09-13T13:00:00Z",
):
    return {
        "flight_number": flight_number,
        "departure_city": departure_city,
        "arrival_city": arrival_city,
        "departure_datetime": departure_datetime,
        "arrival_datetime": arrival_datetime,
    }


def generate_flight_event_json():
    """
    Generates a list of flight event dicts for testing with 12 items.
    - There are 4 direct flights and 4 one-stop journeys possible.
    - There are 3 events that total is 2 journeys that exceed the max duration of 24.
      hours and should be filtered out betwen one-stop and direct flights.
    - There are 3 events on different dates that should be filtered out or layover is greather than 4.
    - There are 2 events that total is 2 journeys direct flights that match the filter and conditions.
    - There are 4 events that total is 2 journeys events one-stop that match the filter and conditions.
    for filter criteria date=datetime(2024, 9, 13), origin="BUE", destination="MAD"
    """
    return [
        create_flight_event_dict(
            flight_number="AR1000",
            departure_datetime=str(datetime(2024, 9, 12, 7, 0).isoformat()),
            arrival_datetime=str(datetime(2024, 9, 12, 15, 0).isoformat()),
        ),
        create_flight_event_dict(
            flight_number="AR1001",
            departure_datetime=str(datetime(2024, 9, 13, 10, 0).isoformat()),
            arrival_datetime=str(datetime(2024, 9, 13, 18, 0).isoformat()),
        ),
        create_flight_event_dict(
            flight_number="AR1002",
            departure_datetime=str(datetime(2024, 9, 13, 5, 0).isoformat()),
            arrival_datetime=str(datetime(2024, 9, 13, 13, 0).isoformat()),
        ),
        create_flight_event_dict(
            flight_number="AR1003",
            departure_datetime=str(datetime(2024, 9, 13, 14, 0).isoformat()),
            arrival_datetime=str(
                datetime(2024, 9, 14, 22, 0).isoformat()
            ),  # More than 24 hours
        ),
        create_flight_event_dict(
            "LA2000",
            "BUE",
            "GRU",
            str(datetime(2024, 9, 12, 6, 0).isoformat()),
            str(datetime(2024, 9, 12, 9, 0).isoformat()),
        ),
        create_flight_event_dict(
            "LA2000",
            "GRU",
            "MAD",
            str(datetime(2024, 9, 12, 14, 0).isoformat()),  # 4 hours layover
            str(datetime(2024, 9, 12, 19, 0).isoformat()),
        ),
        create_flight_event_dict(
            "AA3000",
            "BUE",
            "JFK",
            str(datetime(2024, 9, 13, 8, 0).isoformat()),
            str(datetime(2024, 9, 13, 16, 0).isoformat()),
        ),
        create_flight_event_dict(
            "AA3100",
            "JFK",
            "MAD",
            str(datetime(2024, 9, 13, 18, 0).isoformat()),
            str(datetime(2024, 9, 14, 2, 0).isoformat()),  # 18 flight hours
        ),
        create_flight_event_dict(
            "LA4000",
            "BUE",
            "SCL",
            str(datetime(2024, 9, 13, 9, 0).isoformat()),
            str(datetime(2024, 9, 13, 11, 30).isoformat()),
        ),
        create_flight_event_dict(
            "LA4100",
            "SCL",
            "MAD",
            str(datetime(2024, 9, 13, 13, 0).isoformat()),
            str(datetime(2024, 9, 14, 21, 30).isoformat()),  # more than 24 hours
        ),
        create_flight_event_dict(
            "LA5000",
            "BUE",
            "ATL",
            str(datetime(2024, 9, 13, 5, 0).isoformat()),
            str(datetime(2024, 9, 13, 7, 30).isoformat()),
        ),
        create_flight_event_dict(
            "LA5100",
            "ATL",
            "MAD",
            str(datetime(2024, 9, 13, 9, 0).isoformat()),
            str(datetime(2024, 9, 13, 17, 40).isoformat()),
        ),
    ]
