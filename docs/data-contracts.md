# Data contracts

File schemas for the current cooling-water prototype.

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


## Sources and rights

| Source | Exact download / format | Evidence we have | What it does not show |
| --- | --- | --- | --- |
| USGS Water Data OGC API | `https://api.waterdata.usgs.gov/ogcapi/v1/collections/monitoring-locations/items` and `/daily/items`; HUC prefix and chosen station ID | Two-day river-flow parsing check: USGS-01646500, HUC8 02070008 | A gauge measures one place; it does not show how much water a town can allocate |
| NOAA NCEI GSOD | `https://www.ncei.noaa.gov/access/services/data/v1`; `dataset=global-summary-of-the-day`, chosen station and dates | Two weather readings: GSOD 72403093738, July 1-2, 2024 | Wet-bulb temperature is estimated using a sea-level approximation, not directly measured |
| NOAA nClimDiv | `https://www.ncei.noaa.gov/monitoring-content/data/us/climdiv/monthly/current/`; newest `climdiv-pdsidv` file | Monthly drought-score (PDSI) parser and source filename | Division 4401's location match to the gauge/facility is not validated |
| Made-up facility observations | Fixed-seed generator in `src/demo.py`, 1,600 rows per cooling type | Model comparison and demo forecast | Generated water-use targets cannot prove real-facility accuracy |
| Made-up station readings | 365 dates, a target and two similar neighbors | Missing-data experiment | Random target gaps do not cover multiple stations failing together or extreme readings being more likely to disappear |
| Permit sections | User-supplied JSONL: section, source URL, HUC or coordinate radius | Fictional `example.org` test documents | No real, checked EPA/EIA/municipal collection has been added to search yet |

The observed parsing example used July 1-2, 2024. Preserve units, station IDs,
quality flags, source filenames, and dates. Provisional/estimated flags remain visible;
they are not all automatically rejected by the forecast.

USGS [licensing guidance](https://www.usgs.gov/data-management/data-licensing) and
NOAA's [FAQ](https://www.noaa.gov/office-education/outreach-communication/faq) were checked
on October 7, 2026 for the public products used here. Check each new product's notices,
third-party rights, and permit-sharing terms. The project cites ASHRAE and implements
its own rules; it does not distribute handbook passages. No private accounts,
commercial scraping, surveys, instructor approval, or IRB decision are claimed.
Before expanding to scraping or studies involving people, confirm course/institutional
requirements with the instructor.

The original [evidence manifest](a2/evidence/manifest.json) records commits, seed,
Python version, and SHA-256 fingerprints for the October 7 snapshot. Source hashes
refer to that implementation, not today's refactored files. Selected results are
portable; raw data and trusted model objects stay in ignored data folders.
