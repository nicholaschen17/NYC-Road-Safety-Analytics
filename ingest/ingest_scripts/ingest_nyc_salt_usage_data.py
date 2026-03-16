from shared.config import Config
from shared.db import DB
import requests

# Function to ingest salt usage data
def get_salt_usage_data_from_api():

    config = Config()
    db = DB()
    source_config = config.get_source("salt_usage_data")
    batch_size = source_config["batch_size"]
    app_token = config.get_nyc_app_token()

    headers = {"X-App-Token": app_token}

    with requests.post(
        source_config["api_url"],
        headers=headers,
        stream=True,
        timeout=60,
    ) as response:
        response.raise_for_status()
        db.bulk_insert_json_stream(response, source_config["table"], batch_size)

    return response.status_code

if __name__ == "__main__":
    status_code = get_salt_usage_data_from_api()
    print("Ingested salt usage data from API with status code: ", status_code)
