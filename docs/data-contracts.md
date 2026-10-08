# Data contracts

## Training CSV

One row is one dated facility observation. Required columns:

| Column | Meaning |
| --- | --- |
| `date` | Observation date, ISO format; entire dates stay in the same split |
| `cooling_type` | `direct_evaporative`, `air_cooled`, or `cooling_tower` |
| `facility_mw` | Installed IT capacity in MW, not total site electrical demand |
| `dry_bulb_c` | Ambient dry-bulb °C, in the supported -20 to 50 °C domain |
| `wet_bulb_c` | Ambient wet-bulb °C; must not exceed dry-bulb |
| `historical_streamflow_mgd` | Representative observed station flow in million US gallons/day |
| `pdsi` | NOAA divisional Palmer Drought Severity Index, dimensionless |
| `consumption_mgd` | Independently measured daily on-site cooling consumption target |

`seasonal_factor` may be provided explicitly in [0, 1]; otherwise it is derived from
the observation month with a July maximum and January minimum. Capacity, temperatures,
and season must be complete. Missing flow/PDSI are allowed and imputed with training
medians. At least 30 distinct dates per cooling technology are required.

Example header and rows (two rows alone are insufficient to train):

```csv
date,cooling_type,facility_mw,dry_bulb_c,wet_bulb_c,historical_streamflow_mgd,pdsi,consumption_mgd
2023-07-01,cooling_tower,40,30,20,70,-3,0.210
2023-07-02,cooling_tower,40,31,21,68,-3,0.214
```

Do not label USGS streamflow as facility consumption or train on rule-generated bounds.
The required feature matrix has six columns; cooling type selects a separate fitted
model. Facility identity is not modeled. Temporal validation tests later observations,
not generalization to unseen facilities. A deployment study needs a facility-separated
holdout and representativeness checks in addition to the current temporal split.

Training saves `model.joblib` and `benchmark.json`. The report includes both candidates'
calibration metrics and raw/bounded test MAE, RMSE, R², row counts, split boundaries,
selected estimator, and interval coverage. R² is null for constant targets. Performance
targets are strictly R² > 0.80 and MAE < 0.05 MGD, not enforced by changing predictions.
Only load model/index joblib files from trusted local runs.

## Environmental snapshots

`environment.csv` has one row per HUC and month. Core fields are `huc8`, `month`,
`latitude`, `longitude`, `dry_bulb_c`, `wet_bulb_c`, `historical_streamflow_mgd`, `pdsi`,
`data_kind`, `source_period_start`, and `source_period_end`. Ingestion also preserves
`flow_station_id`, `noaa_station_id`, `climate_division`, and weather/flow record counts.
HUCs are strings. Valid data kinds are `observed` and `synthetic`.

The CLI uses one explicitly selected flow station as the HUC's representative series.
It does not sum upstream and downstream gauges or claim that streamflow is allocatable
municipal supply. Daily records retain gauge-height and groundwater-depth observations
when USGS publishes a daily mean; discrete groundwater site visits are not included in
this daily endpoint. Missing values and source quality flags remain visible in raw CSVs.

Use additional `--station USGS-ID` arguments to ingest same-HUC donors. For neighboring
HUCs, ingest those separately, then align station matrices by date. NOAA GSOD station
selection and climate-division lookup are explicit; the tool does not infer climate
divisions from HUC numbers. Check [NOAA's division catalog](https://psl.noaa.gov/data/correlation/climdivisions.html)
and station metadata when assembling inputs.

Monthly medians retain missing PDSI/flow when no observations are available. Months
without valid temperatures are omitted. Source periods and record counts should be
reviewed before using sparse records as a seasonal scenario. Coordinates represent
the streamflow station, not a watershed centroid. A nearest-station coordinate request
is an approximation and can be misleading near catchment boundaries.

## Permit JSONL

Each line is one extracted, verified source section. Provide `document_id`, `title`,
`section`, `text`, `source_url`, and either `huc8` (a list) or `latitude`, `longitude`, and
`radius_km`. Set `is_example=true` for demonstration documents.

```json
{"document_id":"sample","title":"Example water permit","section":"IV.B","text":"Example cooling-water reporting requirement.","source_url":"https://example.org/permit","huc8":["02070010"],"is_example":true}
```

Convert PDF/HTML permit sections to text and verify section labels before indexing.
The tool does not invent a permit registry, automatically download documents, or treat
a retrieved passage as a compliance decision. Coordinate radius is an explicit source
scope supplied by the operator, not an inferred legal jurisdiction. HUC-scoped excerpts
only match their listed HUCs. Source URLs and section identifiers survive chunking and
index reload. Excerpts are verbatim and may include numbers that the generator never
interprets or compares to the forecast.

## Sensitivity CSVs

- `stations.csv`: `date` followed by one streamflow column per station, values in MGD.
- `coordinates.csv`: `station_id,latitude,longitude`, covering every station column.
- `daily_features.csv`: `date`, the six model features (or month instead of seasonal
  factor), and PDSI for drought identification.

Dates must be unique, sorted, and aligned between station series and feature rows.
The target series must be complete for the reference experiment. Neighbor series may
contain gaps; donors are tried in geographic order. No available donor is an explicit
error. Choose donors with comparable hydrology: nearest geographic distance alone
does not establish interchangeability or justify transferring a groundwater depth.

Outputs distinguish MGD² prediction variance, MGD standard deviation, tolerance
coverage, and per-date empirical 5th/95th percentiles. The band is over random masks,
not a guarantee of 90% accuracy against true facility measurements. Station-wide outages,
contiguous missing blocks, and missing extremes are not represented by this mask model.
Groundwater filling is tested in meters, independently of the MGD forecast sensitivity.
