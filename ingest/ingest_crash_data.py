import os
import requests
import psycopg2
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import io

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Connect to DB
def connect_to_db():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def close_db_connection(conn):
    conn.close()

# Columns that must be integers for raw_data (PostgreSQL INT rejects "2.0" from pandas float)
RAW_DATA_INT_COLUMNS = [
    "zip_code",
    "number_of_persons_injured",
    "number_of_persons_killed",
    "number_of_pedestrians_injured",
    "number_of_pedestrians_killed",
    "number_of_cyclist_injured",
    "number_of_cyclist_killed",
    "number_of_motorist_injured",
    "number_of_motorist_killed",
]


def _normalize_column_names(df):
    """Lowercase and replace spaces with underscores to match schema/COPY."""
    df = df.rename(columns=lambda c: c.strip().lower().replace(" ", "_") if isinstance(c, str) else c)
    return df


def fetch_collisions_data():
    # Temporary placeholder for using collision data from csv file
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # backend/ingest -> backend -> project
    CSV_PATH = os.path.join(PROJECT_ROOT, "backend", "data", "collisions.csv")
    df = pd.read_csv(CSV_PATH)
    df = _normalize_column_names(df)
    # Coerce count columns to int so COPY sends "2" not "2.0" (PostgreSQL INT)
    for col in RAW_DATA_INT_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")
    return df

def bulk_copy_raw_data(df):
    conn = connect_to_db()
    cursor = conn.cursor()

    # Write dataframe to an in-memory CSV buffer
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False, na_rep="\\N")
    buffer.seek(0)

    cursor.copy_expert("""
        COPY raw_data (
            crash_date, crash_time, borough, zip_code,
            latitude, longitude, location, on_street_name,
            cross_street_name, off_street_name, number_of_persons_injured,
            number_of_persons_killed, number_of_pedestrians_injured,
            number_of_pedestrians_killed, number_of_cyclist_injured,
            number_of_cyclist_killed, number_of_motorist_injured,
            number_of_motorist_killed, contributing_factor_vehicle_1,
            contributing_factor_vehicle_2, contributing_factor_vehicle_3,
            contributing_factor_vehicle_4, contributing_factor_vehicle_5,
            collision_id, vehicle_type_code_1, vehicle_type_code_2,
            vehicle_type_code_3, vehicle_type_code_4, vehicle_type_code_5
        )
        FROM STDIN
        WITH (FORMAT csv, NULL '\\N')
    """, buffer)

    conn.commit()
    cursor.close()
    close_db_connection(conn)

def main():
    df = fetch_collisions_data()
    bulk_copy_raw_data(df)

if __name__ == "__main__":
    main()