import requests
from job_orchestrator.db.nyc_data import NYCData
from job_orchestrator.shared.config import Config
from job_orchestrator.shared.db import DB
from shapely.geometry import shape


# Function to ingest street rating data
def get_zone_map_data_from_api():

    config = Config()
    db = NYCData()
    config_name = "zone_map_data"
    source_config = config.get_source(config_name)
    app_token = config.get_nyc_app_token()

    headers = {"X-App-Token": app_token}

    with requests.post(
        source_config["api_url"],
        headers=headers,
        stream=True,
        timeout=60,
    ) as response:
        response.raise_for_status()
        db.bulk_insert(response, config_name)

    return response.status_code


# Function to populate centerpoint zone data for each zone in the raw_zone_map_data table
def populate_centerpoint_zone_data():
    db = (
        DB()
    )  # DB used here for execute/execute_update — NYCData is for bulk_insert only
    config = Config()
    table = config.get_source("zone_map_data")["table"]

    query = f"SELECT id, geometry, zonename FROM {table}"  # nosec B608
    zones = db.execute(query)

    total_zones = len(zones)

    if len(zones) == 0:
        print("No zones to populate centerpoint data for")
        raise ValueError("No zones to populate centerpoint data for")

    for zone in zones:
        try:
            try:
                geometry = shape(zone["geometry"])
            except Exception as e:
                print(f"Error parsing geometry for {zone['zonename']}: {e}")
                continue
            centerpoint = geometry.representative_point()

            # Add lat and long of centerpoint to raw_zone_map_data table
            query = f"UPDATE {table} SET centerpoint_latitude = %s, centerpoint_longitude = %s WHERE id = %s"  # nosec B608
            db.execute_update(query, (centerpoint.y, centerpoint.x, zone["id"]))
            print(
                f"Added centerpoint latitude {centerpoint.y} and longitude {centerpoint.x} to {zone['zonename']}"
            )
        except Exception as e:
            print(
                f"Error adding centerpoint latitude {centerpoint.y} and longitude {centerpoint.x} to {zone['zonename']}: {e}"
            )
            continue


if __name__ == "__main__":
    status_code = get_zone_map_data_from_api()
    print("Ingested zone map data from API with status code: ", status_code)
    populate_centerpoint_zone_data()
    print("Populated centerpoint zone data for all zones")
