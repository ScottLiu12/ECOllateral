# Data contracts: what each input file must contain

These rules keep units, dates, and sources consistent. For a short explanation of
the system and terms, see `a2/explain-it-simply.md`. Exact field names stay unchanged.

## Training CSV

Each row describes one facility observation on one date. Required columns:

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
the observation month, highest in July and lowest in January. Capacity, temperatures,
and season cannot be missing. Missing flow/PDSI can be filled with the median from
the training data. Each cooling technology needs at least 30 different dates.

Example header and rows (two rows alone are insufficient to train):

```csv
date,cooling_type,facility_mw,dry_bulb_c,wet_bulb_c,historical_streamflow_mgd,pdsi,consumption_mgd
2023-07-01,cooling_tower,40,30,20,70,-3,0.210
2023-07-02,cooling_tower,40,31,21,68,-3,0.214
```

USGS river flow is not facility water consumption. Physical limits calculated by rules
are not measured training targets. The model uses six input columns; each cooling type
selects its own trained model. Facility identity is not an input. The current date-based
test checks later observations. To show that the model works at new facilities, reserve
whole facilities for testing and check that the data represent the intended users.

Training saves `model.joblib` and `benchmark.json`. The report keeps both models'
calibration scores, original/physically adjusted test scores, row counts, date boundaries,
chosen model, and prediction-range coverage. MAE is average error size; RMSE weights big
errors more strongly; R² measures fit. R² is null when all target values are the same.
The targets are strictly R² > 0.80 and MAE < 0.05 MGD. Predictions are not changed just
to make those targets pass. Only load model/index joblib files from trusted local runs.

## Environmental snapshots

`environment.csv` has one row per HUC and month. Core fields are `huc8`, `month`,
`latitude`, `longitude`, `dry_bulb_c`, `wet_bulb_c`, `historical_streamflow_mgd`, `pdsi`,
`data_kind`, `source_period_start`, and `source_period_end`. Ingestion also preserves
`flow_station_id`, `noaa_station_id`, `climate_division`, and weather/flow record counts.
HUCs are strings. Valid data kinds are `observed` and `synthetic`.

Choose one flow station to represent each watershed. The command-line tool does not
add upstream and downstream readings together. River flow is not a claim about water
available for a town to allocate. Daily records keep gauge height and groundwater
depth when USGS publishes a daily mean. Separate groundwater site visits are outside
this daily endpoint. Raw CSVs keep missing values and source quality flags visible.

Use additional `--station USGS-ID` arguments for other stations in the same HUC that
can help fill gaps. Download neighboring HUCs separately, then line up station rows by
date. Choose the NOAA GSOD station and climate division explicitly. The tool cannot
derive a climate division from a HUC number. Check [NOAA's division catalog](https://psl.noaa.gov/data/correlation/climdivisions.html)
and station information when preparing inputs.

If a month has no PDSI/flow readings, its monthly median remains missing. Months with
no valid temperatures are left out. Check source dates and reading counts before using
a month with little data as a seasonal scenario. Coordinates identify the river station,
not the center of the watershed. Matching a request to the nearest station is an
approximation and can be misleading near watershed boundaries.

## Permit JSONL

Each line contains one source section whose text and identifiers have been checked. Provide `document_id`, `title`,
`section`, `text`, `source_url`, and either `huc8` (a list) or `latitude`, `longitude`, and
`radius_km`. Set `is_example=true` for demonstration documents.

```json
{"document_id":"sample","title":"Example water permit","section":"IV.B","text":"Example cooling-water reporting requirement.","source_url":"https://example.org/permit","huc8":["02070010"],"is_example":true}
```

Convert PDF/HTML sections to text and check section labels before adding them to search.
The tool does not invent a permit registry or automatically download the documents.
A matching passage is not a compliance decision. The operator supplies the coordinate
radius describing source coverage; the tool does not infer legal jurisdiction. HUC-based
sections match only their listed HUCs. Source URLs and section IDs stay attached when
text is split into chunks and the saved index is reloaded. Quotations keep the exact
words. Any numbers within them are not interpreted or compared with the forecast.

## Sensitivity CSVs

- `stations.csv`: `date` followed by one streamflow column per station, values in MGD.
- `coordinates.csv`: `station_id,latitude,longitude`, covering every station column.
- `daily_features.csv`: `date`, the six model features (or month instead of seasonal
  factor), and PDSI for drought identification.

Dates must be unique, sorted, and match between station readings and model input rows.
The target station needs complete readings for the reference experiment. Nearby stations
may have gaps; the tool tries them in distance order. If none has a usable reading, it
returns an error. Choose stations with similar water behavior. Being nearest does not
make a station interchangeable or justify copying its groundwater depth.

Results separately report variance in MGD², standard deviation in MGD, the share of
changes within tolerance, and each date's 5th/95th percentiles. Variance and standard
deviation describe how much predictions change. The percentile band comes from repeated
random choices of missing readings; it is not a 90% accuracy guarantee against measured
facility water use. These random masks do not cover whole-station outages, long missing
blocks, or extreme readings being more likely to disappear. Groundwater filling stays
in meters and is tested separately from changes in MGD forecasts.
