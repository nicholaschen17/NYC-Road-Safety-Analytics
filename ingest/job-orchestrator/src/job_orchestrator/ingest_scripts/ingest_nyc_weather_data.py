from datetime import date, datetime

import openmeteo_requests
import pandas as pd
import requests_cache
from job_orchestrator.db.weather_data import WeatherData
from job_orchestrator.shared.config import Config
from job_orchestrator.shared.types import WeatherParam, Zone
from retry_requests import retry


def get_latest_weather_data_for_zone(zone: Zone) -> datetime:
    weather_data = WeatherData()
    return weather_data.get_latest_weather_data_for_zone(zone).date()


def get_zones() -> list[Zone]:
    weather_data = WeatherData()
    return weather_data.get_zones()


def generate_weather_params(zone: Zone) -> WeatherParam:
    return WeatherParam(
        latitude=zone["centerpoint_latitude"],
        longitude=zone["centerpoint_longitude"],
        start_date=get_latest_weather_data_for_zone(zone),
        end_date=date.today(),
        hourly=[
            "temperature_2m",
            "precipitation",
            "weather_code",
            "rain",
            "snowfall",
            "apparent_temperature",
            "cloud_cover",
            "snow_depth",
        ],
    )


def retrieve_weather_data(weather_param: WeatherParam) -> pd.DataFrame:
    config = Config()
    source = config.get_source("weather_data")
    cache_session = requests_cache.CachedSession(".cache", expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = source["api_url"]
    responses = openmeteo.weather_api(url, params=weather_param)

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = responses[0].Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()
    hourly_weather_code = hourly.Variables(2).ValuesAsNumpy()
    hourly_rain = hourly.Variables(3).ValuesAsNumpy()
    hourly_snowfall = hourly.Variables(4).ValuesAsNumpy()
    hourly_apparent_temperature = hourly.Variables(5).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(6).ValuesAsNumpy()
    hourly_snow_depth = hourly.Variables(7).ValuesAsNumpy()
    hourly_centerpoint_latitude = weather_param["latitude"]
    hourly_centerpoint_longitude = weather_param["longitude"]

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
    }

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["weather_code"] = hourly_weather_code
    hourly_data["rain"] = hourly_rain
    hourly_data["snowfall"] = hourly_snowfall
    hourly_data["apparent_temperature"] = hourly_apparent_temperature
    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["snow_depth"] = hourly_snow_depth
    hourly_data["centerpoint_latitude"] = hourly_centerpoint_latitude
    hourly_data["centerpoint_longitude"] = hourly_centerpoint_longitude
    hourly_dataframe = pd.DataFrame(data=hourly_data)
    print("\nHourly data\n", hourly_dataframe)
    return hourly_dataframe


def ingest_weather_data(hourly_dataframe: pd.DataFrame):
    weather_data = WeatherData()
    weather_data.ingest_weather_data(hourly_dataframe)


def main():
    zones = get_zones()
    for zone in zones:
        weather_param = generate_weather_params(zone)
        try:
            hourly_dataframe = retrieve_weather_data(weather_param)
        except Exception as e:
            print(f"Error retrieving weather data for zone {zone['id']}: {e}")
            continue
        try:
            ingest_weather_data(hourly_dataframe)
        except Exception as e:
            print(f"Error ingesting weather data for zone {zone['id']}: {e}")
            continue
        print(f"Ingested weather data for zone {zone['id']}")


if __name__ == "__main__":
    main()
