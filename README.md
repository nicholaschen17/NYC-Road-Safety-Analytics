[![Ingest lint](https://github.com/nicholaschen17/NYC-Road-Safety-Analytics/actions/workflows/ingest-lint.yml/badge.svg?branch=main)](https://github.com/nicholaschen17/NYC-Road-Safety-Analytics/actions/workflows/ingest-lint.yml)
# NYC-Road-Safety-Analytics
A crash intelligence system that identifies high-risk areas, times, and contributing factors to identify critical business questions

## Prerequisites

- **Python 3.13** for local development (e.g. the `ingest/` virtualenv). **Do not use Python 3.14** — Dagster, dbt, and related packages do not support it yet.

### Ingest / Dagster (local)

```bash
cd ingest
python3.13 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

The **ingest Docker image** is built on **Python 3.13** (`ingest/Dockerfile`). Behavior should match 3.13 for this project; if you need identical versions everywhere, align the Dockerfile base image with your local Python version.

### Docker Restart / Rebuild
Restart:
```bash
docker compose build dagster_webserver dagster_daemon
docker compose up -d dagster_webserver dagster_daemon
```

Reload:
```bash
docker compose restart dagster_webserver dagster_daemon
```