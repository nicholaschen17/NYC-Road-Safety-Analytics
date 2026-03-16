import ijson
import psycopg2.extras
import requests
from config import Config

config = Config()


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
