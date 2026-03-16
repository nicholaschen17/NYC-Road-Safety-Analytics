# NYC Salt Usage
# https://data.cityofnewyork.us/City-Government/DSNY-Salt-Usage/tavr-zknk/about_data

# Need to match coordinates to salt usage to get the salt usage
import pandas as pd
import os
from sodapy import Socrata
from shared.config import Config
from shared.helper import Helper


config = Config()
helper = Helper()
source_config = config.get_source("salt_usage_data")
app_token = config.get_nyc_app_token()

# Function to ingest salt usage data
def ingest_salt_usage_data():
    # Grabs required information to connect to the NYC Open Data API
    api_code = helper.get_api_code(source_config["nyc_open_data_url"])
    base_nyc_url = helper.get_nyc_url(source_config["api_url"])
    
    # Connects to the NYC Open Data API
    client = Socrata(base_nyc_url, app_token=app_token)
    results = client.get(api_code, limit=2000)

    # Converts the results to a pandas DataFrame
    results_df = pd.DataFrame.from_records(results)
    print(results_df.head())


def main():
    ingest_salt_usage_data()

if __name__ == "__main__":
    main()