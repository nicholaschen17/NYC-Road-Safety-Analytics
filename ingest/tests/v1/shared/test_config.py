import pytest

from shared.config import Config

MINIMAL_SOURCES_YAML = """
sources:
  test_source:
    api_url: https://example.com/api
    table: raw_test
"""


# ── load_sources ──────────────────────────────────────────────────────────────


class TestLoadSources:
    def test_returns_dict(self):
        config = Config()
        assert isinstance(config.sources, dict)

    def test_contains_all_known_sources(self):
        config = Config()
        expected = [
            "crash_data",
            "salt_usage_data",
            "bike_route_data",
            "district_grid_data",
            "moving_violation_data",
            "speed_hump_data",
            "speed_limits_data",
            "street_rating_data",
            "traffic_volume_cnt_data",
            "weather_data",
            "zone_map_data",
        ]
        for source in expected:
            assert source in config.sources, f"'{source}' missing from sources.yml"

    def test_each_source_has_api_url(self):
        config = Config()
        for name, source in config.sources.items():
            assert "api_url" in source, f"'{name}' is missing api_url"

    def test_each_source_has_table(self):
        config = Config()
        for name, source in config.sources.items():
            assert "table" in source, f"'{name}' is missing table"

    def test_raises_file_not_found_for_missing_yaml(self, tmp_path):
        config = Config.__new__(Config)
        config._SOURCES_PATH = str(tmp_path / "nonexistent.yml")
        with pytest.raises(FileNotFoundError):
            config.load_sources()


# ── get_source ────────────────────────────────────────────────────────────────


class TestGetSource:
    def test_returns_dict_for_known_source(self):
        config = Config()
        source = config.get_source("salt_usage_data")
        assert isinstance(source, dict)

    def test_returned_source_has_expected_fields(self):
        config = Config()
        source = config.get_source("salt_usage_data")
        assert "api_url" in source
        assert "table" in source

    def test_raises_key_error_for_unknown_source(self):
        config = Config()
        with pytest.raises(KeyError, match="not found in sources.yml"):
            config.get_source("nonexistent_source")

    def test_error_message_lists_available_sources(self):
        config = Config()
        with pytest.raises(KeyError) as exc_info:
            config.get_source("bad_source_name")
        assert "salt_usage_data" in str(exc_info.value)

    def test_all_known_sources_are_accessible(self):
        config = Config()
        for name in config.sources:
            result = config.get_source(name)
            assert isinstance(result, dict)


# ── get_db_config ─────────────────────────────────────────────────────────────


class TestGetDbConfig:
    def test_uses_postgres_primary_env_vars(self, monkeypatch):
        monkeypatch.setenv("POSTGRES_HOST", "pg-host")
        monkeypatch.setenv("POSTGRES_PORT", "5433")
        monkeypatch.setenv("POSTGRES_DB", "pg-db")
        monkeypatch.setenv("POSTGRES_USER", "pg-user")
        monkeypatch.setenv("POSTGRES_PASSWORD", "pg-pass")

        db = Config().get_db_config()

        assert db["host"] == "pg-host"
        assert db["port"] == "5433"
        assert db["dbname"] == "pg-db"
        assert db["user"] == "pg-user"
        assert db["password"] == "pg-pass"

    def test_falls_back_to_db_prefix_env_vars(self, monkeypatch):
        for var in [
            "POSTGRES_HOST",
            "POSTGRES_DB",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
        ]:
            monkeypatch.delenv(var, raising=False)

        monkeypatch.setenv("DB_HOST", "fallback-host")
        monkeypatch.setenv("DB_NAME", "fallback-db")
        monkeypatch.setenv("DB_USER", "fallback-user")
        monkeypatch.setenv("DB_PASSWORD", "fallback-pass")

        db = Config().get_db_config()

        assert db["host"] == "fallback-host"
        assert db["dbname"] == "fallback-db"
        assert db["user"] == "fallback-user"

    def test_port_defaults_to_5432_when_not_set(self, monkeypatch):
        monkeypatch.delenv("POSTGRES_PORT", raising=False)
        monkeypatch.delenv("DB_PORT", raising=False)

        db = Config().get_db_config()

        assert db["port"] == "5432"

    def test_postgres_port_takes_priority_over_db_port(self, monkeypatch):
        monkeypatch.setenv("POSTGRES_PORT", "5433")
        monkeypatch.setenv("DB_PORT", "9999")

        db = Config().get_db_config()

        assert db["port"] == "5433"

    def test_returns_none_for_unset_credentials(self, monkeypatch):
        for var in [
            "POSTGRES_HOST",
            "DB_HOST",
            "POSTGRES_DB",
            "DB_NAME",
            "POSTGRES_USER",
            "DB_USER",
            "POSTGRES_PASSWORD",
            "DB_PASSWORD",
        ]:
            monkeypatch.delenv(var, raising=False)

        db = Config().get_db_config()

        assert db["host"] is None
        assert db["dbname"] is None
        assert db["user"] is None
        assert db["password"] is None

    def test_return_value_has_exactly_expected_keys(self, monkeypatch):
        db = Config().get_db_config()
        assert set(db.keys()) == {"host", "port", "dbname", "user", "password"}


# ── get_nyc_app_token ─────────────────────────────────────────────────────────


class TestGetNycAppToken:
    def test_returns_token_when_set(self, monkeypatch):
        monkeypatch.setenv("NYC_APP_TOKEN", "abc123token")
        assert Config().get_nyc_app_token() == "abc123token"

    def test_returns_none_when_not_set(self, monkeypatch):
        monkeypatch.delenv("NYC_APP_TOKEN", raising=False)
        assert Config().get_nyc_app_token() is None

    def test_returns_none_for_empty_string(self, monkeypatch):
        monkeypatch.setenv("NYC_APP_TOKEN", "")
        assert Config().get_nyc_app_token() is None
