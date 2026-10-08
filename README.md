# ECOllateral

Ecosystem Collateral Forecast Tool. Estimates how much water a data center uses for
cooling each day. An AI model predicts the number, engineering rules check its physical
limits, and a document search adds permit quotations for the location. Water is measured
in million US gallons per day (MGD).

The model predicts on-site cooling water use. To assess a town's water stress, we would
also need water supply, other withdrawals, water returned to rivers, and ecological
flow needs. Start with the [plain-English explanation](docs/a2/explain-it-simply.md)
for the system steps, experiments, and technical terms.

## Development

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m pytest
```

On systems with Make, `make lint`, `make test`, `make run`, and `make ingest ARGS="..."`
wrap the same Python commands. Activate the virtual environment first, or set
`PYTHON=.venv/Scripts/python.exe` on Windows. Python 3.11 or newer is supported.

## Run the offline demo

```powershell
.venv\Scripts\python -m src.cli demo
$env:ECOLLATERAL_DATA_DIR = (Resolve-Path data/processed/demo).Path
.venv\Scripts\python -m uvicorn src.api.app:app --reload
```

The demo learns from made-up water-use targets and station readings, and uses a fictional
permit. Every forecast labels those sources. It requires no API keys.
Open [interactive API documentation](http://127.0.0.1:8000/docs), or send:

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

`seasonal_target` is a calendar month (1–12). Supply an eight-digit watershed code (HUC),
keeping leading zeros, or both `latitude` and `longitude`. Coordinate lookup chooses
the nearest configured station within 50 km. The response explains that this station
match is an approximation.

The response includes physical limits, the original and adjusted water-use estimates,
R² on test data, a prediction range intended for 90% coverage, source dates, citations,
and warnings. R² measures model fit; it is not the chance a prediction is right.
`predicted_collateral_stress_mgd` is the existing field name for on-site consumption.
It is not a validated measure of a town's water stress.

## Use observed data

To download observed data, choose a USGS river-flow station, NOAA GSOD weather station,
and NOAA climate division. Check that each represents the facility's conditions.
A watershed code (HUC) is different from a NOAA climate division.

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

Set `USGS_API_KEY` if you need authenticated USGS quotas. These NOAA endpoints do not
require a CDO token. A network failure returns an error; the tool does not quietly use
made-up observations instead. The service returns 503 until a model and environmental
snapshots exist. If permit context is missing, the forecast says so.

USGS river flow, gauge height, and daily groundwater depth keep their station IDs and
quality flags. NOAA GSOD temperature and dew point are used to estimate wet-bulb
temperature. Monthly drought scores (PDSI) come from nClimDiv. Monthly median values
describe historical conditions for a scenario; they do not predict future weather.
These environmental downloads do not include the facility's water-use training target.
Training for real-world use needs independently measured facility consumption.

See [data contracts](docs/data-contracts.md) for schemas, training splits, units, and
station selection, and [implementation notes](docs/implementation-notes.md) for detailed
decisions, research sources, and verification results.
The measured local check results and synthetic benchmark tables are recorded in
[validation results](docs/validation-results.md).

## Physical assumptions

Capacity means IT megawatts. By default, all available IT load is assumed in use
(utilization 1.0). PUE is total facility power divided by IT power; the default is 1.2.
Training accepts `--pue`, `--utilization`, and `--evaporative-fraction-max`, and saves those
assumptions with the model. The upper limit uses the heat absorbed by evaporating water
(a latent-heat balance). The lower limit is zero. Dry air cooling excludes added
evaporative assistance (adiabatic assistance). The target excludes domestic uses,
water used to generate grid electricity, and blowdown returned to the watershed.

ASHRAE defines water usage effectiveness (WUE) as liters of site water per kWh of IT
energy and provides heat-management guidance. The adjustable values here are engineering
assumptions, not universal ASHRAE limits. The API returns water per unit of heat energy
(thermal-water intensity) and the corresponding site WUE.
Sources: [ASHRAE data-center handbook](https://handbook.ashrae.org/Handbooks/A23/SI/A23_Ch20/a23_ch20_si.aspx)
and [cooling-tower handbook](https://handbook.ashrae.org/Handbooks/S24/IP/s24_ch40/s24_ch40_ip.aspx).

## Missingness research

```powershell
.venv\Scripts\python -m src.cli sensitivity `
    --stations data/processed/demo/stations.csv `
    --coordinates data/processed/demo/coordinates.csv `
    --features data/processed/demo/daily_features.csv `
    --model data/processed/demo/model.joblib --target target
.venv\Scripts\python scripts/run_notebook.py
```

The notebook is [01_missingness_sensitivity_analysis.ipynb](notebooks/01_missingness_sensitivity_analysis.ipynb).
Its default run uses the synthetic demo. Set `ECOLLATERAL_RESEARCH_DIR` and
`ECOLLATERAL_TARGET_STATION` to analyze observed MGD station series with a trusted model.
It exports tables, figures, and an executed notebook into ignored processed-data folders.

The experiment removes 10%, 25%, and 40% of target-station drought readings. Repeated
tests compare borrowing from a nearby station with filling gaps along a straight line
through time. A fixed seed makes the repeats reproducible. Results report how much
predictions change (variance) and central 90% change bands against a ±0.05 MGD limit.
Groundwater filling is tested separately in meters. Using it instead of river flow
would require a measured relationship between groundwater and flow.

## Client and checks

`src/client/forecast.ts` exports a typed `forecastFacility` fetch function and
`ForecastError`. It works in browser or modern Node runtimes; no frontend is required.

```powershell
npm ci --ignore-scripts
npm run typecheck
.venv\Scripts\python -m ruff check src tests scripts
.venv\Scripts\python -m ruff format --check src tests scripts
.venv\Scripts\python -m pytest
```

Offline tests cover ingestion through the API, physical bounds, train-only imputation,
artifact reload, citation geography, and stable/unstable missingness cases. GitHub Actions
runs lint, tests, and TypeScript checking when changes are pushed.

## CSCI 4150 mid-semester review

The [A2 package](docs/a2/README.md) includes the project checkoff, an eight-page
project evidence review, system diagram showing how information is represented,
experiment tables and failure cases,
editable six-slide presentation, four-minute script, and proposed team responsibilities.
It separates synthetic benchmarks from field evidence and lists the course actions
that still need confirmation. Start with `docs/a2/dossier.pdf` or the package index.
