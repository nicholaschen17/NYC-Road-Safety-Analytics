import requests

from shared.config import Config
from db.nyc_data import NYCData


# Function to ingest bike route data
def get_bike_route_data_from_api():

    config = Config()
    db = NYCData()
    config_name = "bike_route_data"
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


if __name__ == "__main__":
    status_code = get_bike_route_data_from_api()
    print("Ingested bike route data from API with status code: ", status_code)
