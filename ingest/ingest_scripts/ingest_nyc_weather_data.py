import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from shared.config import Config
from shared.types import WeatherParam
from datetime import date

config = Config()
SOURCE = config.get_source("weather_data")



def ingest_weather_data(weather_param: WeatherParam):
	cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
	retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
	openmeteo = openmeteo_requests.Client(session=retry_session)

	url = SOURCE["api_url"]
	params = {
		# Latitude and longitude can be lists for mulitple locations
		"latitude": 52.52,
		"longitude": 13.41,
		"start_date": "2026-01-24",
		"end_date": "2026-01-25",
		# Hourly is where we specify the weather variables we want to return.
		"hourly": ["temperature_2m", "precipitation", "weather_code", "rain", "snowfall", "apparent_temperature", "cloud_cover", "snow_depth"],
	}
	responses = openmeteo.weather_api(url, params=params)

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
	hourly_data = {"date": pd.date_range(
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
		end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	)}

	hourly_data["temperature_2m"] = hourly_temperature_2m
	hourly_data["precipitation"] = hourly_precipitation
	hourly_data["weather_code"] = hourly_weather_code
	hourly_data["rain"] = hourly_rain
	hourly_data["snowfall"] = hourly_snowfall
	hourly_data["apparent_temperature"] = hourly_apparent_temperature
	hourly_data["cloud_cover"] = hourly_cloud_cover
	hourly_data["snow_depth"] = hourly_snow_depth
	hourly_dataframe = pd.DataFrame(data = hourly_data)
	print("\nHourly data\n", hourly_dataframe)


def main():
	weather_param = WeatherParam(
		latitude=52.52,
		longitude=13.41,
		start_date=date(2026, 1, 24),
		end_date=date(2026, 1, 25),
		hourly=["temperature_2m", "precipitation", "weather_code", "rain", "snowfall", "apparent_temperature", "cloud_cover", "snow_depth"],
	)
	ingest_weather_data(weather_param)

if __name__ == "__main__":
	main()