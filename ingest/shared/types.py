from datetime import date
from typing import TypedDict


class WeatherParam(TypedDict):
    latitude: float | list[float]
    longitude: float | list[float]
    start_date: date
    end_date: date
    hourly: list[str]

class Zone(TypedDict):
    id: str
    centerpoint_latitude: float
    centerpoint_longitude: float