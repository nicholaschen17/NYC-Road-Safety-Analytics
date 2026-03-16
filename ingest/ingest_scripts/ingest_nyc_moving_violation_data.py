"""
Error where 
  File "/Users/nicholaschen/Desktop/NYC-Road-Safety-Analytics/ingest/venv/lib/python3.14/site-packages/psycopg2/extras.py", line 1299, in execute_values
    cur.execute(b''.join(parts))
    ~~~~~~~~~~~^^^^^^^^^^^^^^^^^
psycopg2.errors.SyntaxError: syntax error at or near "@"
LINE 1: ...rd_cd, y_coord_cd, latitude, longitude, juris_cd, @computed_...
"""

# import requests

# from shared.config import Config
# from shared.db import DB

# # Function to ingest moving violation data
# def get_moving_violation_data_from_api():

#     config = Config()
#     db = DB()
#     config_name = "moving_violation_data"
#     source_config = config.get_source(config_name)
#     app_token = config.get_nyc_app_token()

#     headers = {"X-App-Token": app_token}

#     with requests.post(
#         source_config["api_url"],
#         headers=headers,
#         stream=True,
#         timeout=60,
#     ) as response:
#         response.raise_for_status()
#         db.bulk_insert(response, config_name)

#     return response.status_code


# if __name__ == "__main__":
#     status_code = get_moving_violation_data_from_api()
#     print("Ingested moving violation data from API with status code: ", status_code)
