import json
from decimal import Decimal

import ijson
import psycopg2
import psycopg2.extras
import requests
from job_orchestrator.shared.config import Config


class NYCData:
    def __init__(self):
        self.config = Config()

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
    def _bulk_insert_json_stream(
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

        api_keys = [k for k in first_row.keys() if "@" not in k]
        columns = [k.lstrip(":") for k in api_keys]
        col_list = ", ".join(columns)
        insert_sql = f"INSERT INTO {table} ({col_list}) VALUES %s ON CONFLICT DO NOTHING"  # nosec B608

        conn = psycopg2.connect(**self.config.get_db_config())
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

    def _iter_geojson_rows(self, response):
        response.raw.decode_content = True
        for feature in ijson.items(response.raw, "features.item"):
            # Flatten: merge properties with geometry as WKT/GeoJSON string
            row = feature.get("properties") or {}
            row["geometry"] = json.dumps(feature.get("geometry"), cls=_DecimalEncoder)
            yield row

    def _bulk_insert_geojson_stream(
        self, response: requests.Response, table: str, batch_size: int
    ):
        row_iter = self._iter_geojson_rows(response)

        first_row = next(row_iter, None)
        if first_row is None:
            print("No rows to insert.")
            return

        api_keys = [k for k in first_row.keys() if "@" not in k]
        columns = [k.lstrip(":") for k in api_keys]
        col_list = ", ".join(columns)
        insert_sql = f"INSERT INTO {table} ({col_list}) VALUES %s ON CONFLICT DO NOTHING"  # nosec B608

        conn = psycopg2.connect(**self.config.get_db_config())
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

    def bulk_insert(self, response: requests.Response, config_name: str):
        # Given a response determine GeoJSON or JSON from the format key in the source config
        format = self.config.get_source(config_name)["format"]
        batch_size = self.config.get_source(config_name)["batch_size"]
        table = self.config.get_source(config_name)["table"]

        if format == "GeoJSON":
            return self._bulk_insert_geojson_stream(response, table, batch_size)
        elif format == "JSON":
            return self._bulk_insert_json_stream(response, table, batch_size)
        else:
            raise ValueError(f"Invalid format: {format}")


class _DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)
