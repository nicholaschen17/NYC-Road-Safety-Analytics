from urllib.parse import urlparse


class Helper:
    def __init__(self):
        pass

    def get_api_code(self, url: str) -> str:
        parts = urlparse(url).path.split("/")
        return parts[-2]

    def get_nyc_url(self, url: str) -> str:
        return urlparse(url).netloc
