from typing import TypedDict
from datetime import date

class WeatherParam(TypedDict):
    latitude: float | list[float]
    longitude: float | list[float]
    start_date: date
    end_date: date
    hourly: list[str]


