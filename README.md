# ECOllateral

A course prototype for studying development's effects on regional water conditions.
The implemented component estimates daily on-site cooling consumption in million US
gallons (MGD), combines USGS/NOAA observations with physical limits, and retrieves
location-matched permit quotations. It does not yet calculate municipal reserves or a
validated ecosystem stress score.

The project uses Python, FastAPI, pandas, RandomForest/XGBoost, and word matching for permits.
A small TypeScript fetch client is included; there is no frontend or hosted AI service.
[Data contracts](docs/data-contracts.md) describe inputs, units, and splits.

## Setup and checks

Python 3.11 or newer is supported. From the repository root:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m ruff check src tests scripts
.venv\Scripts\python -m ruff format --check src tests scripts
.venv\Scripts\python -m pytest
npm ci --ignore-scripts
npm run typecheck
```

On systems with Make, activate the environment or set `PYTHON=.venv/Scripts/python.exe`.
`make lint`, `make test`, `make run`, and `make ingest ARGS="..."` wrap these commands.
GitHub Actions runs Python checks and TypeScript checking.

## Offline demo and API

```powershell
.venv\Scripts\python -m src.cli demo
$env:ECOLLATERAL_DATA_DIR = (Resolve-Path data/processed/demo).Path
.venv\Scripts\python -m uvicorn src.api.app:app --reload
```

The demo uses synthetic station readings and water-use targets, plus a fictional
permit. Forecasts label these sources. No API keys are needed.
See [interactive API documentation](http://127.0.0.1:8000/docs), or send:

```powershell
$request = @{
    facility_mw = 40
    cooling_type = "cooling_tower"
    huc8 = "02070010"
    seasonal_target = 7
} | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/forecast -Method Post `
    -ContentType application/json -Body $request
```

`seasonal_target` is a calendar month, 1–12. Supply an eight-digit watershed code
(HUC8), preserving leading zeros, or both `latitude` and `longitude`. Coordinates
match the nearest configured station within 50 km; this is an approximation.
Monthly conditions are historical medians, not forecasts of future weather.

Responses include physical limits, raw and adjusted consumption, held-out R²,
a nominal 90% prediction interval, source dates, citations, and warnings.
`predicted_collateral_stress_mgd` is the existing name for on-site consumption.
R² measures fit, not the chance a prediction is correct. The service returns 503
until model and environmental artifacts exist; missing permit context is reported.
`src/client/forecast.ts` exports `forecastFacility` and `ForecastError` for browsers
and modern Node runtimes.

## Observed data

Choose representative USGS and NOAA stations and a NOAA climate division. A HUC8
is not a climate division. Environmental downloads do not provide the facility's
water-use target; real training requires independently measured consumption.

```powershell
.venv\Scripts\python -m src.cli ingest --huc8 YOUR_HUC8 `
    --flow-station USGS-YOUR_STATION --noaa-station YOUR_11_DIGIT_GSOD_ID `
    --climate-division YOUR_4_DIGIT_DIVISION `
    --start 2020-01-01 --end 2024-12-31
.venv\Scripts\python -m src.cli train --input path/to/measured_facility_records.csv
.venv\Scripts\python -m src.cli index-permits --input path/to/permit_sections.jsonl
Remove-Item Env:ECOLLATERAL_DATA_DIR -ErrorAction SilentlyContinue
.venv\Scripts\python -m uvicorn src.api.app:app
```

Set `USGS_API_KEY` for authenticated USGS quotas. These NOAA endpoints need no CDO
token. Network failures raise errors. USGS station IDs and quality flags are retained;
GSOD temperature/dew point estimate wet-bulb temperature, and nClimDiv supplies PDSI.
Only load model and index joblib files from trusted local runs.

Capacity means IT MW. Default physical assumptions are PUE 1.2, utilization 1.0,
and maximum evaporative fraction 1.0; override them with training's `--pue`,
`--utilization`, and `--evaporative-fraction-max`. Bounds use a latent-heat balance
and exclude grid water, domestic uses, and returned blowdown. Dry cooling assumes
no evaporative assistance. These are screening assumptions, not universal ASHRAE
limits. See [implementation notes](docs/implementation-notes.md) for reasoning and
references, and [validation results](docs/validation-results.md) for recorded evidence.

## Missingness experiment

```powershell
.venv\Scripts\python -m src.cli sensitivity `
    --stations data/processed/demo/stations.csv `
    --coordinates data/processed/demo/coordinates.csv `
    --features data/processed/demo/daily_features.csv `
    --model data/processed/demo/model.joblib --target target
.venv\Scripts\python scripts/run_notebook.py
```

The [notebook](notebooks/01_missingness_sensitivity_analysis.ipynb) compares nearest
station filling and time interpolation after masking 10%, 25%, and 40% of drought
readings. Seeded repeats report variance and central 90% change bands against a
±0.05 MGD tolerance. Groundwater reconstruction is separate and stays in meters.
Set `ECOLLATERAL_RESEARCH_DIR` and `ECOLLATERAL_TARGET_STATION` for observed inputs
and a trusted model. Tables, plots, and executed notebooks go into ignored data folders.

## Regional assessment and course materials

The broader goal is to assess development's effects on seasonal water reserves and
watershed conditions for planners, researchers, and utilities. That requires measured
supply, demand, return flows, and ecological baselines, plus checked station and utility
boundaries. Training and evaluation need measured facility consumption and separate
model-selection, calibration, and test sets, including unseen facilities and areas.
Regional balances, recharge and heatwave studies, neural models, dense embeddings,
and language-model comparisons remain future work.

The [A2 package](docs/a2/README.md) contains the checkoff, evidence review, system map,
editable six-slide presentation, talk, and assigned team responsibilities. Results
in the package describe the October 7, 2026 synthetic experiments.
