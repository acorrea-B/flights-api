from os import getenv


class ConfigVars:
    FLIGHT_EVENTS_API_URL: str = getenv(
        "FLIGHT_EVENTS_API_URL",
        "https://mock.apidog.com/m1/814105-793312-default/flight-events",
    )
    MAX_JOURNEY_DURATION_HOURS: int = int(getenv("MAX_JOURNEY_DURATION_HOURS", "24"))
    MAX_LAYOVER_HOURS: int = int(getenv("MAX_LAYOVER_HOURS", "4"))
    MIN_LAYOVER_HOURS: int = int(getenv("MIN_LAYOVER_HOURS", "1"))
    DEFAULT_API_TIMEOUT: int = int(getenv("DEFAULT_API_TIMEOUT", "10"))
