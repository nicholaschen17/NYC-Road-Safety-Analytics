FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgeos-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/          shared/
COPY db/              db/
COPY ingest_scripts/  ingest_scripts/
COPY dagster/ingest_coordination_dagster/  dagster/ingest_coordination_dagster/
COPY sources.yml      sources.yml
COPY dagster/workspace.yaml  workspace.yaml
COPY dagster/dagster.yaml    dagster.yaml

ENV PYTHONPATH="/app:/app/dagster"
ENV DAGSTER_HOME=/app