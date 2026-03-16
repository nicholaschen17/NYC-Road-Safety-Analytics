PYTHON     := venv/bin/python
PIP        := venv/bin/pip
PYTEST     := venv/bin/pytest
BLACK      := venv/bin/black
ISORT      := venv/bin/isort
AUTOFLAKE  := venv/bin/autoflake
BANDIT     := venv/bin/bandit
INGEST_DIR := ingest_scripts

.DEFAULT_GOAL := help

# ── environment ───────────────────────────────────────────────────────────────

.PHONY: venv
venv: ## Create virtual environment
	python3 -m venv venv

.PHONY: install
install: venv ## Install all dependencies into the venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# ── linting ───────────────────────────────────────────────────────────────────

.PHONY: lint
lint: ## Format and lint all source files (black → isort → autoflake → bandit)
	$(BLACK)     ./ingest_scripts ./tests ./shared
	$(ISORT)     ./ingest_scripts ./tests ./shared
	$(AUTOFLAKE) --in-place --remove-all-unused-imports -r ./ingest_scripts ./tests ./shared
	$(BANDIT)    -r ./ingest_scripts ./shared

.PHONY: black
black: ## Format with black
	$(BLACK) ./ingest_scripts ./tests ./shared

.PHONY: isort
isort: ## Sort imports with isort
	$(ISORT) ./ingest_scripts ./tests ./shared

.PHONY: autoflake
autoflake: ## Remove unused imports with autoflake
	$(AUTOFLAKE) --in-place --remove-all-unused-imports -r ./ingest_scripts ./tests ./shared

.PHONY: bandit
bandit: ## Run bandit security scan
	$(BANDIT) -r ./ingest_scripts ./shared

# ── testing ───────────────────────────────────────────────────────────────────

.PHONY: test
test: ## Run all tests
	$(PYTEST) tests/ -v

.PHONY: test-shared
test-shared: ## Run shared/ unit tests only
	$(PYTEST) tests/v1/shared/ -v

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	$(PYTEST) tests/ -v --cov=shared --cov=ingest_scripts --cov-report=term-missing

# ── ingest scripts ────────────────────────────────────────────────────────────

.PHONY: ingest-all
ingest-all: ## Run all ingest scripts sequentially
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_crash_data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_salt_usage_data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_weather_data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_bike_route_data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_district_grid_data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_moving_violation_data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_speed_hump_data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_speed_limits_data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_street_rating_data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_traffic_volume_cnt_data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_zone_map_data

.PHONY: ingest-crash
ingest-crash: ## Ingest NYC crash data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_crash_data

.PHONY: ingest-salt
ingest-salt: ## Ingest NYC salt usage data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_salt_usage_data

.PHONY: ingest-weather
ingest-weather: ## Ingest NYC weather data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_weather_data

.PHONY: ingest-bike
ingest-bike: ## Ingest NYC bike route data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_bike_route_data

.PHONY: ingest-district
ingest-district: ## Ingest NYC district grid data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_district_grid_data

.PHONY: ingest-violations
ingest-violations: ## Ingest NYC moving violation data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_moving_violation_data

.PHONY: ingest-speed-humps
ingest-speed-humps: ## Ingest NYC speed hump data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_speed_hump_data

.PHONY: ingest-speed-limits
ingest-speed-limits: ## Ingest NYC speed limits data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_speed_limits_data

.PHONY: ingest-street-rating
ingest-street-rating: ## Ingest NYC street rating data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_street_rating_data

.PHONY: ingest-traffic
ingest-traffic: ## Ingest NYC traffic volume count data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_traffic_volume_cnt_data

.PHONY: ingest-zones
ingest-zones: ## Ingest NYC zone map data
	$(PYTHON) -m $(INGEST_DIR).ingest_nyc_zone_map_data

# ── database ──────────────────────────────────────────────────────────────────

.PHONY: db-init
db-init: ## Apply schema.sql to the database (requires DB env vars to be set)
	psql "host=$${POSTGRES_HOST} port=$${POSTGRES_PORT:-5432} dbname=$${POSTGRES_DB} user=$${POSTGRES_USER} password=$${POSTGRES_PASSWORD}" \
		-f ../db/schema.sql

.PHONY: db-reset
db-reset: ## Drop all raw tables and re-apply schema (DESTRUCTIVE)
	@echo "WARNING: This will drop all raw tables. Press Ctrl-C to cancel."
	@sleep 3
	psql "host=$${POSTGRES_HOST} port=$${POSTGRES_PORT:-5432} dbname=$${POSTGRES_DB} user=$${POSTGRES_USER} password=$${POSTGRES_PASSWORD}" \
		-c "DROP TABLE IF EXISTS raw_crash_data, raw_salt_usage_data, raw_weather_data, \
		    raw_bike_route_data, raw_district_grid_data, raw_moving_violation_data, \
		    raw_speed_hump_data, raw_speed_limits_data, raw_street_rating_data, \
		    raw_traffic_volume_cnt_data, raw_zone_map_data CASCADE;"
	$(MAKE) db-init

# ── cleanup ───────────────────────────────────────────────────────────────────

.PHONY: clean
clean: ## Remove __pycache__ and .pyc files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true

.PHONY: clean-venv
clean-venv: ## Remove the virtual environment entirely
	rm -rf venv

# ── help ──────────────────────────────────────────────────────────────────────

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'
