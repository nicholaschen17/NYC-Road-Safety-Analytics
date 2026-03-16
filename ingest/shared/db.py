import json, io, psycopg2
import pandas as pd
from shared.config import Config

config = Config()

def connect_to_db():
    conn = psycopg2.connect(**config.get_db_config())
    return conn

def bulk_insert_from_json(json_data: list[dict], table: str, columns: list[str]):
    # 1. JSON → DataFrame
    df = pd.DataFrame(json_data)[columns]

    # 2. DataFrame → in-memory CSV buffer
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False, na_rep="\\N")
    buffer.seek(0)

    # 3. Stream buffer into Postgres via COPY
    conn = psycopg2.connect(**config.get_db_config())
    cursor = conn.cursor()
    cols = ", ".join(columns)
    cursor.copy_expert(f"""
        COPY {table} ({cols})
        FROM STDIN
        WITH (FORMAT csv, NULL '\\N')
    """, buffer)
    conn.commit()
    cursor.close()
    conn.close()