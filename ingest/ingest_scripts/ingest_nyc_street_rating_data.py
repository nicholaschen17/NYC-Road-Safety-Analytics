import requests

from db.nyc_data import NYCData
from shared.config import Config


# Function to ingest street rating data
def get_street_rating_data_from_api():

    config = Config()
    db = NYCData()
    config_name = "street_rating_data"
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
    status_code = get_street_rating_data_from_api()
    print("Ingested street rating data from API with status code: ", status_code)
