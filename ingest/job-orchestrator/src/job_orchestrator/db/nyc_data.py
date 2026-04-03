import itertools
import json
from decimal import Decimal

import ijson
import psycopg2
import psycopg2.extras
import requests
from job_orchestrator.shared.config import Config

# Rows scanned upfront to discover the full column set from sparse JSON.
# Socrata omits keys entirely for NULL fields, so we need a sample large
# enough to observe optional columns (e.g. borough, latitude) which may be
# absent from the first few records.
_SCHEMA_DISCOVERY_ROWS = 5_000

# Max rows per individual SQL INSERT statement.  Decoupled from batch_size
# (which controls commit frequency) so we never send a single statement large
# enough to crash the server.
_SQL_PAGE_SIZE = 1_000


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

        Column names are inferred from the union of keys across the first batch
        rather than only the first row. Socrata uses sparse JSON — optional fields
        like borough/latitude/longitude are omitted entirely when NULL — so
        inferring from a single row would silently drop those columns if the first
        record happens to have no location data.
        """

        row_iter = self._iter_json_rows(response)

        # Sample the first _SCHEMA_DISCOVERY_ROWS rows to build the full column
        # set. Socrata uses sparse JSON — optional fields like borough/latitude
        # are omitted entirely on NULL rows, so inferring from one row alone
        # silently drops those columns for the entire load.
        discovery: list[dict] = []
        all_keys: set[str] = set()
        for row in row_iter:
            discovery.append(row)
            all_keys.update(k for k in row.keys() if "@" not in k)
            if len(discovery) >= _SCHEMA_DISCOVERY_ROWS:
                break

        if not discovery:
            print("No rows to insert.")
            return

        api_keys = sorted(all_keys)
        columns = [k.lstrip(":") for k in api_keys]
        col_list = ", ".join(columns)
        insert_sql = f"INSERT INTO {table} ({col_list}) VALUES %s ON CONFLICT DO NOTHING"  # nosec B608

        def _serialize(v):
            return json.dumps(v, cls=_DecimalEncoder) if isinstance(v, (dict, list)) else v

        conn = psycopg2.connect(**self.config.get_db_config())
        try:
            cursor = conn.cursor()
            total = 0
            batch: list = []

            # Chain discovery rows back in so nothing is skipped, then stream
            # the rest.  _SQL_PAGE_SIZE caps the SQL statement size regardless
            # of how large each application-level batch is.
            for row in itertools.chain(discovery, row_iter):
                batch.append([_serialize(row.get(k)) for k in api_keys])
                if len(batch) >= batch_size:
                    psycopg2.extras.execute_values(
                        cursor, insert_sql, batch, page_size=_SQL_PAGE_SIZE
                    )
                    conn.commit()
                    total += len(batch)
                    print(f"Inserted {total} rows so far...")
                    batch = []

            if batch:
                psycopg2.extras.execute_values(
                    cursor, insert_sql, batch, page_size=_SQL_PAGE_SIZE
                )
                conn.commit()
                total += len(batch)

            cursor.close()
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
            cursor = conn.cursor()
            total = 0
            batch = [[first_row.get(k) for k in api_keys]]
            for row in row_iter:
                batch.append([row.get(k) for k in api_keys])
                if len(batch) >= _SQL_PAGE_SIZE:
                    psycopg2.extras.execute_values(
                        cursor, insert_sql, batch, page_size=_SQL_PAGE_SIZE
                    )
                    conn.commit()
                    total += len(batch)
                    print(f"Inserted {total} rows so far...")
                    batch = []

            if batch:
                psycopg2.extras.execute_values(
                    cursor, insert_sql, batch, page_size=_SQL_PAGE_SIZE
                )
                conn.commit()
                total += len(batch)

            cursor.close()
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
