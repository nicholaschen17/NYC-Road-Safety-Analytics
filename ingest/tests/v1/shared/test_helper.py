import pytest
from shared.helper import Helper


@pytest.fixture
def helper():
    return Helper()


class TestGetApiCode:
    def test_standard_socrata_json_url(self, helper):
        url = "https://data.cityofnewyork.us/api/v3/views/h9gi-nx95/query.json"
        assert helper.get_api_code(url) == "h9gi-nx95"

    def test_standard_socrata_geojson_url(self, helper):
        url = "https://data.cityofnewyork.us/api/v3/views/mzxg-pwib/query.geojson"
        assert helper.get_api_code(url) == "mzxg-pwib"

    def test_returns_second_to_last_path_segment(self, helper):
        # generic case: always returns segment at [-2]
        url = "https://example.com/a/b/DATASET_CODE/rows.json"
        assert helper.get_api_code(url) == "DATASET_CODE"

    def test_different_dataset_codes(self, helper):
        codes = ["tavr-zknk", "i6mn-amj2", "57p3-pdcj", "7ym2-wayt"]
        for code in codes:
            url = f"https://data.cityofnewyork.us/api/v3/views/{code}/query.json"
            assert helper.get_api_code(url) == code


class TestGetNycUrl:
    def test_standard_socrata_url(self, helper):
        url = "https://data.cityofnewyork.us/api/v3/views/h9gi-nx95/query.json"
        assert helper.get_nyc_url(url) == "data.cityofnewyork.us"

    def test_open_meteo_url(self, helper):
        url = "https://archive-api.open-meteo.com/v1/archive"
        assert helper.get_nyc_url(url) == "archive-api.open-meteo.com"

    def test_strips_path_and_query(self, helper):
        url = "https://example.com/some/deep/path?foo=bar"
        assert helper.get_nyc_url(url) == "example.com"

    def test_url_with_port(self, helper):
        url = "http://localhost:5432/some/path"
        assert helper.get_nyc_url(url) == "localhost:5432"

    def test_returns_only_netloc_not_scheme(self, helper):
        url = "https://data.cityofnewyork.us/path"
        result = helper.get_nyc_url(url)
        assert "https" not in result
        assert "://" not in result
