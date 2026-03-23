One place for ops: DB health, container-ish signals, queue depth, disk — if you add Prometheus (or similar) and scrape exporters.
Logs in one UI: Loki + Grafana for searching errors across dagster_daemon, APIs, etc.
Business / data KPIs in SQL: dashboards over crash_data_postgres (row counts, freshness, null rates, “last ingest”) — Grafana is fine as a SQL dashboard if you don’t want to build that in the app or Dagster alone.
Alerting: “no successful run in 24h,” “table not updated,” SLO-style alerts (usually needs metrics or a query datasource + alert rules).