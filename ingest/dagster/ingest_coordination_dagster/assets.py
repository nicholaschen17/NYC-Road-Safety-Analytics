
import requests
from shapely.geometry import shape
from dagster import asset, AssetExecutionContext, Output
from ingest_coordination_dagster.resources import NYCDataResource, WeatherDataResource, SourceConfigResource

def build_nyc_open_data_asset(config_name: str, group_name: str = "raw_nyc_data"):
    """
    Factory that generates a Dagster asset for any NYC Open Data source.
    Replaces the boilerplate in each ingest_nyc_*_data.py script.
    """

    @asset(
        name=f"raw_{config_name}",
        group_name=group_name,
        description=f"Raw {config_name} from NYC Open Data API",
    )
    def _asset(
        context: AssetExecutionContext,
        nyc_data: NYCDataResource,
        source_config: SourceConfigResource,
    ):
        config = source_config.create_client()
        db = nyc_data.create_client()
        source = config.get_source(config_name)
        app_token = config.get_nyc_app_token()

        headers = {"X-App-Token": app_token}

        with requests.post(
            source["api_url"],
            headers=headers,
            stream=True,
            timeout=60,
        ) as response:
            response.raise_for_status()
            db.bulk_insert(response, config_name)

        context.log.info(f"Ingested {config_name} successfully")

    return _asset


# Generate assets for all standard NYC Open Data sources
crash_data_asset = build_nyc_open_data_asset("crash_data")
salt_usage_asset = build_nyc_open_data_asset("salt_usage_data")
bike_route_asset = build_nyc_open_data_asset("bike_route_data")
district_grid_asset = build_nyc_open_data_asset("district_grid_data")
moving_violation_asset = build_nyc_open_data_asset("moving_violation_data")
speed_hump_asset = build_nyc_open_data_asset("speed_hump_data")
speed_limits_asset = build_nyc_open_data_asset("speed_limits_data")
street_rating_asset = build_nyc_open_data_asset("street_rating_data")
traffic_volume_asset = build_nyc_open_data_asset("traffic_volume_cnt_data")

@asset(
    group_name="raw_nyc_data",
    description="Raw zone map GeoJSON from NYC Open Data",
)
def raw_zone_map_data(
    context: AssetExecutionContext,
    nyc_data: NYCDataResource,
    source_config: SourceConfigResource,
):
    config = source_config.create_client()
    db = nyc_data.create_client()
    source = config.get_source("zone_map_data")
    app_token = config.get_nyc_app_token()

    headers = {"X-App-Token": app_token}
    with requests.post(
        source["api_url"], headers=headers, stream=True, timeout=60
    ) as response:
        response.raise_for_status()
        db.bulk_insert(response, "zone_map_data")

    context.log.info("Ingested zone map data")


@asset(
    group_name="raw_nyc_data",
    deps=[raw_zone_map_data],
    description="Zone map enriched with centerpoint lat/lon computed from geometry",
)
def zone_map_centerpoints(
    context: AssetExecutionContext,
    source_config: SourceConfigResource,
):
    """Reuses your existing populate_centerpoint_zone_data logic."""
    from shared.db import DB

    db = DB()
    config = source_config.create_client()
    table = config.get_source("zone_map_data")["table"]

    zones = db.execute(f"SELECT id, geometry, zonename FROM {table}")
    if not zones:
        raise ValueError("No zones found — cannot compute centerpoints")

    for zone in zones:
        try:
            geometry = shape(zone["geometry"])
            centerpoint = geometry.representative_point()
            db.execute_update(
                f"UPDATE {table} SET centerpoint_latitude = %s, centerpoint_longitude = %s WHERE id = %s",
                (centerpoint.y, centerpoint.x, zone["id"]),
            )
            context.log.info(f"Centerpoint for {zone['zonename']}: ({centerpoint.y}, {centerpoint.x})")
        except Exception as e:
            context.log.warning(f"Skipped {zone['zonename']}: {e}")

@asset(
    group_name="raw_weather",
    deps=[zone_map_centerpoints],
    description="Hourly weather data per zone from Open-Meteo, depends on zone centerpoints",
)
def raw_weather_data(
    context: AssetExecutionContext,
    weather_data_resource: WeatherDataResource,
    source_config: SourceConfigResource,
):
    """Mirrors the logic of ingest_nyc_weather_data.py main()."""
    from ingest_scripts.ingest_nyc_weather_data import (
        generate_weather_params,
        retrieve_weather_data,
    )

    wd = weather_data_resource.create_client()
    zones = wd.get_zones()
    context.log.info(f"Fetching weather for {len(zones)} zones")

    for zone in zones:
        try:
            params = generate_weather_params(zone)
            df = retrieve_weather_data(params)
            wd.ingest_weather_data(df)
            context.log.info(f"Ingested weather for zone {zone['id']}")
        except Exception as e:
            context.log.warning(f"Failed zone {zone['id']}: {e}")