import os
import yaml
from dotenv import load_dotenv

load_dotenv()

_SOURCES_PATH = os.path.join(os.path.dirname(__file__), "sources.yml")


def load_sources() -> dict:
    """Load all source configs from sources.yml."""
    with open(_SOURCES_PATH) as f:
        return yaml.safe_load(f)["sources"]


def get_source(name: str) -> dict:
    """Return config for a single named source. Raises KeyError if not found."""
    sources = load_sources()
    if name not in sources:
        raise KeyError(f"Source '{name}' not found in sources.yml. Available: {list(sources.keys())}")
    return sources[name]


def get_db_config() -> dict:
    """Return DB connection config from environment variables."""
    return {
        "host": os.getenv("POSTGRES_HOST", os.getenv("DB_HOST")),
        "port": os.getenv("POSTGRES_PORT", os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("POSTGRES_DB", os.getenv("DB_NAME")),
        "user": os.getenv("POSTGRES_USER", os.getenv("DB_USER")),
        "password": os.getenv("POSTGRES_PASSWORD", os.getenv("DB_PASSWORD")),
    }


def get_nyc_app_token() -> str | None:
    """Return NYC Open Data app token if set (optional but avoids rate limits)."""
    return os.getenv("NYC_OPEN_DATA_APP_TOKEN")
