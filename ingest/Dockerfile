FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgeos-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml .
COPY job-orchestrator/src/job_orchestrator/ ./job_orchestrator/
COPY job-orchestrator/src/dbt_orchestrator/ ./dbt_orchestrator/
COPY job-orchestrator/workspace.yaml  workspace.yaml
COPY job-orchestrator/dagster.yaml    dagster/dagster.yaml
COPY transform/ ./transform/

# Install job_orchestrator + dbt_orchestrator into site-packages so Dagster gRPC
# code servers always resolve imports (PYTHONPATH + working_directory alone can be flaky).
RUN pip install --no-cache-dir -e .

ENV PYTHONPATH="/app"
ENV DAGSTER_HOME=/app