import requests
import psycopg2
import pandas as pd
from shared.config import Config
from shared.helper import Helper


config = Config()
helper = Helper()
source_config = config.get_source("salt_usage_data")
app_token = config.get_nyc_app_token()

headers = {"X-App-Token": app_token}

payload = {
    "serializationOptions": {
        "separator": ",",
        "bom": False  # Set to False for cleaner DB ingestion
    }
} 

with requests.post(
    source_config["api_url"],
    headers=headers,
    json=payload
) as response:
    response.raise_for_status()
    # Convert response to DataFrame
    df = pd.DataFrame(response.json())
    print(df.head())