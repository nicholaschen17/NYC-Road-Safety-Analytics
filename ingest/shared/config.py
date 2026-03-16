import os

import yaml
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self._SOURCES_PATH = self._SOURCES_PATH = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "sources.yml"
        )
        self.sources = self.load_sources()

    def load_sources(self) -> dict:
        """Load all source configs from sources.yml."""
        with open(self._SOURCES_PATH) as f:
            return yaml.safe_load(f)["sources"]

    def get_source(self, name: str):
        if name not in self.sources:
            raise KeyError(
                f"Source '{name}' not found in sources.yml. Available: {list(self.sources.keys())}"
            )
        return self.sources[name]

    def get_db_config(self) -> dict:
        return {
            "host": os.getenv("POSTGRES_HOST", os.getenv("DB_HOST")),
            "port": os.getenv("POSTGRES_PORT", os.getenv("DB_PORT", "5432")),
            "dbname": os.getenv("POSTGRES_DB", os.getenv("DB_NAME")),
            "user": os.getenv("POSTGRES_USER", os.getenv("DB_USER")),
            "password": os.getenv("POSTGRES_PASSWORD", os.getenv("DB_PASSWORD")),
        }

    def get_nyc_app_token(self) -> str | None:
        return os.getenv("NYC_APP_TOKEN") if os.getenv("NYC_APP_TOKEN") else None
