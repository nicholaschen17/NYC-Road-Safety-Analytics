from datetime import datetime

import pandas as pd
import psycopg2
import psycopg2.extras
from job_orchestrator.shared.config import Config
from job_orchestrator.shared.db import DB
from job_orchestrator.shared.types import Zone


class WeatherData:
    def __init__(self):
        self.config = Config()
        self.db = DB()
        self.weather_table = self.config.get_source("weather_data")["table"]
        self.zone_table = self.config.get_source("zone_map_data")["table"]

    def get_latest_weather_data_for_zone(self, zone: Zone) -> datetime:
        query = f"""
            SELECT
                COALESCE(
                    MAX(weather_timestamp),
                    '2000-01-01 00:00:00'::TIMESTAMP
                ) as most_recent_timestamp
            FROM {self.weather_table}
            WHERE centerpoint_latitude = %s AND centerpoint_longitude = %s
        """
        return self.db.execute(
            query, (zone["centerpoint_latitude"], zone["centerpoint_longitude"])
        )[0]["most_recent_timestamp"]

    def get_zones(self) -> list[Zone]:
        query = f"SELECT id, centerpoint_latitude, centerpoint_longitude FROM {self.zone_table}"
        return self.db.execute(query)

    def ingest_weather_data(self, hourly_dataframe: pd.DataFrame):
        insert_sql = f"""
            INSERT INTO {self.weather_table}
                (weather_timestamp, temperature_2m, precipitation, weather_code, rain, snowfall,
                 apparent_temperature, cloud_cover, snow_depth, centerpoint_latitude, centerpoint_longitude)
            VALUES %s
            ON CONFLICT DO NOTHING
        """
        rows = [
            (
                row["date"].to_pydatetime(),
                row["temperature_2m"],
                row["precipitation"],
                row["weather_code"],
                row["rain"],
                row["snowfall"],
                row["apparent_temperature"],
                row["cloud_cover"],
                row["snow_depth"],
                row["centerpoint_latitude"],
                row["centerpoint_longitude"],
            )
            for _, row in hourly_dataframe.iterrows()
        ]
        conn = psycopg2.connect(**self.config.get_db_config())
        try:
            with conn.cursor() as cursor:
                psycopg2.extras.execute_values(
                    cursor, insert_sql, rows, page_size=10_000
                )
            conn.commit()
            print(f"Inserted {len(rows)} weather rows.")
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
