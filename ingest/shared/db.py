import ijson
import psycopg2.extras
import requests

from shared.config import Config

config = Config()


class DB:
    def __init__(self):
        self.config = Config()

    # Private method to iterate over JSON rows
    def _iter_json_rows(self, response: requests.Response):
        """
        Incrementally parses a streaming JSON array response using ijson.

        Yields one dict per row without ever loading the full payload into memory —
        critical for multi-million row datasets. The response must be opened with
        stream=True so the body isn't buffered upfront by requests.
        """
        response.raw.decode_content = True  # decompress gzip/deflate on the fly
        for row in ijson.items(response.raw, "item"):
            yield row

    # Public method to bulk insert JSON stream into DB (Unsure about GeoJSON format)
    def bulk_insert_json_stream(
        self, response: requests.Response, table: str, batch_size: int
    ):
        """
        Streams a JSON array response and bulk-inserts into Postgres in batches.

        Uses ijson to parse rows incrementally (constant memory regardless of
        response size), then flushes each batch via execute_values — a single
        multi-row INSERT per batch rather than one query per row.

        Column names are inferred from the first row of the stream so no
        hardcoded column list is required.
        """

        row_iter = self._iter_json_rows(response)

        first_row = next(row_iter, None)
        if first_row is None:
            print("No rows to insert.")
            return

        api_keys = list(first_row.keys())
        columns = [k.lstrip(":") for k in api_keys]
        col_list = ", ".join(columns)
        insert_sql = f"INSERT INTO {table} ({col_list}) VALUES %s ON CONFLICT DO NOTHING"  # nosec B608

        conn = psycopg2.connect(**config.get_db_config())
        try:
            with conn.cursor() as cursor:
                batch = [[first_row.get(k) for k in api_keys]]
                total = 0
                for row in row_iter:
                    batch.append([row.get(k) for k in api_keys])
                    if len(batch) >= batch_size:
                        psycopg2.extras.execute_values(
                            cursor, insert_sql, batch, page_size=batch_size
                        )
                        total += len(batch)
                        print(f"Inserted {total} rows so far...")
                        batch = []

                if batch:  # flush remaining rows that didn't fill a full batch
                    psycopg2.extras.execute_values(
                        cursor, insert_sql, batch, page_size=batch_size
                    )
                    total += len(batch)

            conn.commit()
            print(f"Done. Inserted {total} total rows into '{table}'.")
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
