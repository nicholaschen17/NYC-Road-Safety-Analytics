from dagster import ConfigurableResource, EnvVar
from db.nyc_data import NYCData
from db.weather_data import WeatherData
from shared.config import Config


class NYCDataResource(ConfigurableResource):
    """Dagster resource wrapping the existing NYCData bulk-insert logic."""

    def create_client(self) -> NYCData:
        return NYCData()


class WeatherDataResource(ConfigurableResource):
    """Dagster resource wrapping the existing WeatherData query/insert logic."""

    def create_client(self) -> WeatherData:
        return WeatherData()


class SourceConfigResource(ConfigurableResource):
    """Dagster resource wrapping sources.yml config."""

    nyc_app_token: str = ""  # can use EnvVar("NYC_APP_TOKEN")

    def create_client(self) -> Config:
        return Config()