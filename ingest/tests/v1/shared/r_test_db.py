import pytest
from unittest.mock import MagicMock, patch, call

# db.py executes Config() at module level; patch psycopg2.connect so no real
# DB connection is attempted during import or in any test.
with patch("psycopg2.connect"):
    from shared.db import connect_to_db, bulk_insert_from_json


DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "testdb",
    "user":   "testuser",
    "password": "testpass",
}


def _make_mock_conn():
    """Return a (mock_conn, mock_cursor) pair wired up as psycopg2 would."""
    mock_cursor = MagicMock()
    mock_conn   = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


# ── connect_to_db ─────────────────────────────────────────────────────────────

class TestConnectToDb:
    @patch("shared.db.psycopg2.connect")
    @patch("shared.db.config.get_db_config", return_value=DB_CONFIG)
    def test_calls_psycopg2_connect_with_config(self, mock_get_db_config, mock_connect):
        connect_to_db()
        mock_connect.assert_called_once_with(**DB_CONFIG)

    @patch("shared.db.psycopg2.connect")
    @patch("shared.db.config.get_db_config", return_value=DB_CONFIG)
    def test_returns_the_connection_object(self, mock_get_db_config, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        result = connect_to_db()

        assert result is mock_conn


# ── bulk_insert_from_json ─────────────────────────────────────────────────────

COLUMNS = ["id", "storm", "total_tons"]
ROWS = [
    {"id": "1", "storm": "Storm 1", "total_tons": "14620"},
    {"id": "2", "storm": "Storm 2", "total_tons": "9000"},
]


class TestBulkInsertFromJson:
    @patch("shared.db.psycopg2.connect")
    def test_calls_copy_expert(self, mock_connect):
        mock_conn, mock_cursor = _make_mock_conn()
        mock_connect.return_value = mock_conn

        bulk_insert_from_json(ROWS, "raw_salt_usage_data", COLUMNS)

        mock_cursor.copy_expert.assert_called_once()

    @patch("shared.db.psycopg2.connect")
    def test_sql_contains_table_name(self, mock_connect):
        mock_conn, mock_cursor = _make_mock_conn()
        mock_connect.return_value = mock_conn

        bulk_insert_from_json(ROWS, "raw_salt_usage_data", COLUMNS)

        sql = mock_cursor.copy_expert.call_args[0][0]
        assert "raw_salt_usage_data" in sql

    @patch("shared.db.psycopg2.connect")
    def test_sql_contains_all_columns(self, mock_connect):
        mock_conn, mock_cursor = _make_mock_conn()
        mock_connect.return_value = mock_conn

        bulk_insert_from_json(ROWS, "raw_salt_usage_data", COLUMNS)

        sql = mock_cursor.copy_expert.call_args[0][0]
        for col in COLUMNS:
            assert col in sql

    @patch("shared.db.psycopg2.connect")
    def test_csv_buffer_contains_row_values(self, mock_connect):
        mock_conn, mock_cursor = _make_mock_conn()
        mock_connect.return_value = mock_conn

        captured = {}
        def capture(sql, buf):
            captured["content"] = buf.read()

        mock_cursor.copy_expert.side_effect = capture
        bulk_insert_from_json(ROWS, "raw_salt_usage_data", COLUMNS)

        assert "Storm 1" in captured["content"]
        assert "14620"   in captured["content"]
        assert "Storm 2" in captured["content"]

    @patch("shared.db.psycopg2.connect")
    def test_csv_buffer_has_no_header_row(self, mock_connect):
        """DataFrame.to_csv is called with header=False — column names must not appear as a data row."""
        mock_conn, mock_cursor = _make_mock_conn()
        mock_connect.return_value = mock_conn

        captured = {}
        def capture(sql, buf):
            captured["content"] = buf.read()

        mock_cursor.copy_expert.side_effect = capture
        bulk_insert_from_json(ROWS, "raw_salt_usage_data", COLUMNS)

        # The first CSV line should be a data value, not a column name
        first_line = captured["content"].splitlines()[0]
        for col in COLUMNS:
            assert col not in first_line

    @patch("shared.db.psycopg2.connect")
    def test_null_values_serialized_as_backslash_n(self, mock_connect):
        mock_conn, mock_cursor = _make_mock_conn()
        mock_connect.return_value = mock_conn

        captured = {}
        def capture(sql, buf):
            captured["content"] = buf.read()

        mock_cursor.copy_expert.side_effect = capture
        rows_with_null = [{"id": "1", "storm": None, "total_tons": "10"}]
        bulk_insert_from_json(rows_with_null, "raw_salt_usage_data", COLUMNS)

        assert r"\N" in captured["content"]

    @patch("shared.db.psycopg2.connect")
    def test_only_requested_columns_written_to_buffer(self, mock_connect):
        """Extra keys in JSON rows must not appear in the CSV."""
        mock_conn, mock_cursor = _make_mock_conn()
        mock_connect.return_value = mock_conn

        captured = {}
        def capture(sql, buf):
            captured["content"] = buf.read()

        mock_cursor.copy_expert.side_effect = capture
        rows_with_extra = [{"id": "1", "storm": "S1", "total_tons": "10", "extra": "DROP TABLE"}]
        bulk_insert_from_json(rows_with_extra, "raw_salt_usage_data", COLUMNS)

        assert "DROP TABLE" not in captured["content"]

    @patch("shared.db.psycopg2.connect")
    def test_commits_after_copy(self, mock_connect):
        mock_conn, mock_cursor = _make_mock_conn()
        mock_connect.return_value = mock_conn

        bulk_insert_from_json(ROWS, "raw_salt_usage_data", COLUMNS)

        mock_conn.commit.assert_called_once()

    @patch("shared.db.psycopg2.connect")
    def test_closes_cursor_and_connection(self, mock_connect):
        mock_conn, mock_cursor = _make_mock_conn()
        mock_connect.return_value = mock_conn

        bulk_insert_from_json(ROWS, "raw_salt_usage_data", COLUMNS)

        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("shared.db.psycopg2.connect")
    def test_empty_rows_list_does_not_raise(self, mock_connect):
        mock_conn, mock_cursor = _make_mock_conn()
        mock_connect.return_value = mock_conn

        bulk_insert_from_json([], "raw_salt_usage_data", COLUMNS)

        mock_cursor.copy_expert.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch("shared.db.psycopg2.connect")
    def test_correct_row_count_in_buffer(self, mock_connect):
        mock_conn, mock_cursor = _make_mock_conn()
        mock_connect.return_value = mock_conn

        captured = {}
        def capture(sql, buf):
            captured["content"] = buf.read()

        mock_cursor.copy_expert.side_effect = capture
        bulk_insert_from_json(ROWS, "raw_salt_usage_data", COLUMNS)

        lines = [l for l in captured["content"].splitlines() if l.strip()]
        assert len(lines) == len(ROWS)
