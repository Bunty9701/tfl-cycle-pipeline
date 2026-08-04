# TfL Santander Cycles — Automated Data Pipeline

An end-to-end ETL pipeline that automatically extracts live Santander Cycles (London's public bike hire scheme) station data from the Transport for London Unified API every hour, transforms it into a clean structured format, and loads it into a queryable database — with zero manual intervention.

## Business Question

London's Santander Cycles network has ~800 docking stations across the city. Understanding how bike and dock availability fluctuates by station, time of day, and day of week can help identify rebalancing needs (stations that empty out or fill up predictably), inform demand patterns, and surface operational insights — the same kind of problem transport operators, city planners, and logistics teams solve daily.

## Architecture

```
TfL Unified API  →  Python (extract + parse)  →  CSV snapshot  →  SQLite / SQL database  →  Power BI dashboard
       ↑
GitHub Actions (hourly cron schedule, fully automated)
```

1. **Extract**: A Python script calls the TfL `/BikePoint` endpoint, which returns live status for all ~800 docking stations.
2. **Transform**: Raw nested JSON (bike/dock counts are buried in an `additionalProperties` array) is parsed into a clean tabular format: station ID, name, coordinates, bikes available, empty docks, total docks, and a UTC timestamp.
3. **Load**: Each run saves a timestamped CSV, which is loaded into a SQL database (SQLite for prototyping; Azure SQL for the production version) for querying.
4. **Automate**: A GitHub Actions workflow runs this process every hour on a cron schedule, with no manual triggering required, and commits each new snapshot back to this repository.
5. **Visualise**: A Power BI dashboard (in progress) will surface station-level and time-based patterns.

## Why This Project

This mirrors a real ETL workflow I built professionally at Gallops Systems and Solutions (automated reporting pipelines using Python, APIs, and Airflow) — here rebuilt end-to-end using a free public UK data source, GitHub Actions as a lightweight scheduler, and a fully public, verifiable commit history so anyone can see the pipeline actually running.

## Tech Stack

- **Python** — `requests` (API calls), `pandas` (data transformation), `sqlite3` (database load)
- **TfL Unified API** — live, free, London transport open data
- **GitHub Actions** — cron-based scheduling and automation (no server required)
- **SQL** — querying and aggregation
- **Power BI** — dashboard and visualisation *(in progress)*

## Repository Structure

```
tfl-cycle-pipeline/
├── .github/workflows/
│   └── pull_data.yml      # GitHub Actions workflow: runs hourly, calls extract_tfl.py, commits results
├── data/
│   └── bikepoint_*.csv    # Timestamped snapshots, one per hourly run
├── extract_tfl.py         # Core extract–transform–load script
└── README.md
```

## How It Works

### `extract_tfl.py`
- Reads the TfL API key securely from an environment variable (`TFL_APP_KEY`), never hardcoded.
- Calls `GET https://api.tfl.gov.uk/BikePoint`.
- Parses each station's nested `additionalProperties` list into flat fields (`bikes_available`, `empty_docks`, `total_docks`).
- Saves the result as a timestamped CSV in `data/`.

### `.github/workflows/pull_data.yml`
- Triggers on a cron schedule (`0 * * * *` — every hour, on the hour) and can also be triggered manually.
- Spins up a fresh Ubuntu environment, installs dependencies, runs the extract script.
- Commits and pushes the new CSV back to this repository automatically.

## Sample Insight (SQL)

```sql
SELECT
    station_name,
    COUNT(*) AS num_snapshots,
    AVG(bikes_available) AS avg_bikes,
    MIN(bikes_available) AS min_bikes,
    MAX(bikes_available) AS max_bikes
FROM bikepoint_snapshots
GROUP BY station_name
ORDER BY avg_bikes DESC
LIMIT 10;
```
This surfaces which stations consistently run high or low on bike availability — a first step toward identifying rebalancing needs.

## Status

🟢 **Live and running** — pipeline pulls fresh data every hour automatically. Check the [`data/`](./data) folder and commit history for live evidence of the pipeline running.

- [x] API extraction and parsing
- [x] SQLite load and SQL querying
- [x] Full automation via GitHub Actions
- [ ] Migrate to Azure SQL
- [ ] Power BI dashboard
- [ ] Weather-correlation analysis (join with a public weather API to explore demand drivers)

## What I'd Improve With More Time

- Move from SQLite to a proper cloud data warehouse (Azure SQL / BigQuery) for scalability.
- Add data quality checks (e.g. alert if a scheduled run returns fewer than expected stations).
- Orchestrate with Airflow instead of GitHub Actions cron for more production-grade scheduling, retries, and monitoring.

## Author

Shubham Shinde — Data Analyst | [LinkedIn](#) | London, UK
