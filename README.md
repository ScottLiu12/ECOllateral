# ECOllateral

Ecosystem Collateral Forecast Tool. Estimates daily on-site cooling water consumption
in million US gallons per day (MGD), constrains predictions with an engineering heat
balance, and attaches local regulatory excerpts.

The regression target is cooling water consumption. Assessing municipal water stress
also requires supply, other withdrawals, return flows, and ecological flow requirements.

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

The demo trains on an invented response surface and uses synthetic station records and
a fictional permit. Every forecast labels those sources. It requires no API keys.
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

`seasonal_target` is a calendar month (1–12). Supply an eight-digit HUC, preserving
leading zeros, or both `latitude` and `longitude`. Coordinate lookup uses the nearest
configured representative station within 50 km and reports that approximation.

The response includes bounds, raw and constrained consumption, held-out R², a nominal
90% prediction interval, source periods, citations, and warnings. The requested field
`predicted_collateral_stress_mgd` represents the on-site consumption proxy, not a
municipal water-stress index. R² is a fit metric, not a confidence probability.

## Use observed data

Ingestion requires an explicit USGS streamflow station, NOAA GSOD station, and NOAA
climate division. Verify their relevance to the facility; a HUC is not a NOAA division.

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

Set `USGS_API_KEY` for authenticated USGS quotas if needed. NOAA endpoints used here
do not require a CDO token. Network failures remain errors rather than silently falling
back to synthetic observations. The service returns 503 until a model and environmental
snapshots exist; missing permit grounding is reported in the forecast.

USGS streamflow, gauge height, and daily groundwater-depth observations retain station
IDs and quality flags. NOAA GSOD temperatures/dew point produce an approximate wet-bulb;
monthly PDSI comes from nClimDiv. Monthly medians are historical scenario inputs, not a
forecast of future weather. Ingestion cannot supply the supervised consumption target;
training needs independently measured facility records.

See [data contracts](docs/data-contracts.md) for schemas, training splits, units, and
station selection, and [implementation notes](docs/implementation-notes.md) for detailed
decisions, research sources, and verification results.
The measured local check results and synthetic benchmark tables are recorded in
[validation results](docs/validation-results.md).

## Physical assumptions

Capacity means IT MW. The default screening load assumes full utilization and PUE 1.2.
Training accepts `--pue`, `--utilization`, and `--evaporative-fraction-max`, and saves those
assumptions with the model. The evaporation ceiling uses a latent-heat balance; the
lower bound is zero. Dry air cooling excludes adiabatic assistance. The target excludes
domestic uses, indirect grid water consumption, and blowdown returned to the watershed.

ASHRAE defines WUE in L/site-water per kWh of IT energy and provides thermal guidance;
the configurable coefficients here are engineering assumptions, not universal ASHRAE
limits. The API returns both thermal-water intensity and corresponding site WUE.
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

The experiment removes 10%, 25%, and 40% of target-station observations during drought
windows, compares nearest-station and linear time filling over seeded replicates, and
reports prediction variance and empirical 90% sensitivity bands against ±0.05 MGD.
Groundwater reconstruction is evaluated separately in meters; it cannot be substituted
for streamflow in the regression without a calibrated hydrologic relationship.

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
