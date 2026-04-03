import ijson
import psycopg2
import psycopg2.extras
import requests
from job_orchestrator.shared.config import Config
from job_orchestrator.shared.helper import Helper

BATCH_SIZE = 10_000

# Maps Socrata colon-prefixed API keys → Postgres column names
COLUMN_MAP = {
    ":id": "id",
    ":version": "version",
    ":created_at": "created_at",
    ":updated_at": "updated_at",
    "dsny_storm": "dsny_storm",
    "date_of_report": "date_of_report",
    "manhattan": "manhattan",
    "bronx": "bronx",
    "brooklyn": "brooklyn",
    "queens": "queens",
    "staten_island": "staten_island",
    "total_tons": "total_tons",
}
COLUMNS = list(COLUMN_MAP.values())

config = Config()
helper = Helper()
source_config = config.get_source("salt_usage_data")
app_token = config.get_nyc_app_token()

headers = {"X-App-Token": app_token}


def iter_json_rows(response: requests.Response):
    """
    Incrementally parses a streaming JSON array response using ijson.

    Yields one dict per row without ever loading the full payload into memory —
    critical for multi-million row datasets. The response must be opened with
    stream=True so the body isn't buffered upfront by requests.
    """
    response.raw.decode_content = True  # decompress gzip/deflate on the fly
    for row in ijson.items(response.raw, "item"):
        yield row


def bulk_insert_json_stream(response: requests.Response, table: str):
    """
    Streams a JSON array response and bulk-inserts into Postgres in batches.

    Uses ijson to parse rows incrementally (constant memory regardless of
    response size), then flushes each batch via execute_values — a single
    multi-row INSERT per batch rather than one query per row.
    """
    col_list = ", ".join(COLUMNS)
    insert_sql = f"INSERT INTO {table} ({col_list}) VALUES %s ON CONFLICT DO NOTHING"  # nosec B608

    conn = psycopg2.connect(**config.get_db_config())
    try:
        with conn.cursor() as cursor:
            batch = []
            total = 0
            for row in iter_json_rows(response):
                batch.append([row.get(api_key) for api_key in COLUMN_MAP])
                if len(batch) >= BATCH_SIZE:
                    psycopg2.extras.execute_values(
                        cursor, insert_sql, batch, page_size=BATCH_SIZE
                    )
                    total += len(batch)
                    print(f"Inserted {total} rows so far...")
                    batch = []

            if batch:  # flush remaining rows that didn't fill a full batch
                psycopg2.extras.execute_values(
                    cursor, insert_sql, batch, page_size=BATCH_SIZE
                )
                total += len(batch)

        conn.commit()
        print(f"Done. Inserted {total} total rows into '{table}'.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    with requests.post(
        source_config["api_url"],
        headers=headers,
        stream=True,
        timeout=60,
    ) as response:
        response.raise_for_status()
        bulk_insert_json_stream(response, source_config["table"])
