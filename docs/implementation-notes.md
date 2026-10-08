# Implementation notes

## 2026-10-07 — Scope and repository setup

- Starting point: `main`, three README-only commits, no application or existing tests.
  Remote: `https://github.com/ScottLiu12/ECOllateral.git`.
- The brief requests Python ingestion, physical bounds, tabular regression, drought
  missingness experiments, permit retrieval, and a FastAPI endpoint. Keep the requested
  directories at the repository root; the checkout is already named ECOllateral.
- Use a small typed TypeScript HTTP client for downstream consumers; no frontend is
  specified. Avoid introducing a UI or LLM orchestration framework.
- Commit each coherent piece, with notes updated at the same time. Local commits are
  authorized by the user. No push or deployment is requested.
- First commit: package metadata, Make commands, importable modules, ignored runtime
  artifacts, and development instructions.
- The sandbox marks `.git` read-only, so local Git writes require tool escalation.
  The first authorized escalation succeeded. No GitHub credentials were needed.
- The Microsoft Store Python launcher was inaccessible inside the sandbox. Inspect
  the bundled runtime before choosing a working local environment.

## Research and modeling decisions

- ASHRAE's data-center handbook defines WUE as liters of site water per kWh of IT
  energy. It does **not** establish universal per-technology WUE or PUE limits.
  Physical screening must distinguish this definition from liters per thermal kWh.
- Use an explicit heat-balance envelope, with capacity defined as IT power, configurable
  utilization and PUE. The evaporative ceiling uses latent heat of vaporization. Zero
  is the conservative lower bound because hybrid operation and heat reuse can avoid
  evaporation. Air-cooled means dry heat rejection without adiabatic assist.
- Scope of the target: daily on-site cooling consumption, excluding grid water use,
  domestic uses, and tower blowdown returned to the watershed. A municipal water-stress
  assessment needs more hydrology and allocation data than the six requested features.
- Train separate models by cooling technology because cooling type is absent from the
  required six-feature matrix. Do not pool unlike facilities and then rely on clipping
  to repair an ambiguous target.
- Report held-out R² as a fit metric, never as a probability or confidence interval.
  A synthetic benchmark can test mechanics but cannot validate real-world accuracy.
- USGS provides modern OGC REST collections. Discover sites by HUC, then query daily
  streamflow (`00060`), gauge height (`00065`), and groundwater depth (`72019`) by site.
  Retain station identity and quality flags; do not add gauges together as basin supply.
- NOAA GSOD supplies temperature, dew point, and precipitation, not PDSI or observed
  wet-bulb. Derive approximate RH/wet-bulb with an explicit validity range; use monthly
  nClimDiv PDSI with a separately supplied climate-division ID. HUCs and NOAA divisions
  are different geographies and must not be treated as interchangeable.
- Grounding will use FAISS over local TF-IDF vectors, without an embedding service or
  download. Restrict excerpts by geography before ranking. Narratives quote indexed
  text and format the already calculated forecast; they perform no risk arithmetic.

### Primary references consulted

- [ASHRAE data centers, WUE definition](https://handbook.ashrae.org/Handbooks/A23/SI/A23_Ch20/a23_ch20_si.aspx)
- [ASHRAE cooling-tower heat transfer](https://handbook.ashrae.org/Handbooks/S24/IP/s24_ch40/s24_ch40_ip.aspx)
- [USGS OGC getting started](https://api.waterdata.usgs.gov/docs/ogcapi/)
- [USGS migration and field names](https://api.waterdata.usgs.gov/docs/ogcapi/migration/)
- [NOAA Access Data Service](https://www.ncei.noaa.gov/access/search/documentation/data-service/)
- [NOAA GSOD dataset](https://www.ncei.noaa.gov/access/search/datasets/global-summary-of-the-day/)
- [NOAA nClimDiv files](https://www.ncei.noaa.gov/pub/data/cirs/climdiv/)
- [Stull (2011), wet-bulb approximation](https://doi.org/10.1175/JAMC-D-11-0143.1)

### Validation plan

Test conversions and bounds at zero/large loads, invalid psychrometric inputs,
ingestion pagination and missing-value sentinels, training without preprocessing
leakage, raw and clipped predictions, drought-only masks at all requested rates,
nearest-station fallback, interval coverage, geographic citation filtering, artifact
reload, and the offline ingestion-to-API pipeline. Execute the notebook and type-check
the client once the core passes. Keep external-service checks separate from offline
tests, and record failures or unverified behavior rather than inventing results.

## 2026-10-07 — Bounds, features, and ingestion

- Committed the engineering bounds and feature validation as `17105c1`.
- Bound calculation: `IT MW × 1000 × 24 × utilization × PUE` produces thermal kWh/day;
  multiply by `3600 / (2501 - 2.361 × max(wet_bulb_c, 0))` L/thermal-kWh, then divide
  by 3,785,411.784 L/million US gallons. The evaporative fraction is configurable.
  Both evaporative technologies share a conservative all-latent-heat ceiling; this
  is an envelope, not a claim that either technology always operates at that ceiling.
- Dry cooling has zero on-site evaporation under the declared scope. All technologies
  have zero lower bounds. Flag freezing and very small wet-bulb depression for review.
- Feature checks reject missing capacity/temperatures/season, negative flow, infinities,
  and wet-bulb above dry-bulb. Only streamflow and PDSI permit missing values, which
  will be imputed using statistics learned from the training partition.
- Seasonal factor uses `0.5 × (1 + cos(2π(month - 7)/12))`; this assumes Northern
  Hemisphere seasonality, consistent with the USGS/US NOAA implementation.
- USGS observations stay in long form with station ID, HUC, parameter code, converted
  value, units, coordinates, approval status, and qualifiers. Streamflow converts from
  cfs using 0.64631688969744 MGD/cfs; levels convert feet to meters. Negative groundwater
  depths can be valid, so only documented sentinel-scale values are removed there.
- Pagination follows server links, detects loops, limits the page count, and prevents
  API-key forwarding to another host. Empty datasets and HTTP failures are distinct.
- NOAA ingestion explicitly requests standard units, then converts F to C and inches
  to mm. Missing TEMP/DEWP 9999.9 and PRCP 99.99 are not treated as observations.
- Wet-bulb is estimated from temperature/dew point using approximate RH and Stull's
  sea-level equation. Invalid dew point and out-of-domain or cold/dry estimates become
  missing; saturated air uses the exact wet-bulb = dry-bulb identity.
- Monthly PDSI is read from the newest listed nClimDiv divisional file. The climate
  division is supplied explicitly. Missing -99.99 values remain missing.
- Environment: created `.venv` using the bundled Python 3.12 runtime. Network-restricted
  dependency installation failed with Windows socket error 10013; the authorized
  dependency-download escalation succeeded. This did not require GitHub access.
- First targeted test run: **17 passed** (bounds and mocked NOAA/USGS ingestion).
  Initial Ruff check caught three long lines; automatic formatting handled wrapping.

## 2026-10-07 — Regression and uncertainty design

- Fit RandomForest and XGBoost independently for each cooling type. Require at least
  30 distinct dates per type, and assign entire dates to chronological 60/20/20
  train/calibration/test partitions. No date straddles two partitions.
- Choose the candidate on calibration RMSE; reserve the final test period for reporting.
  Record candidate raw and physically clipped metrics separately. Do not refit on the
  calibration/test period after choosing a winner.
- Keep raw forecast, clipped forecast, warnings, and fitted feature ranges. Missing
  features and extrapolation generate visible warnings. Synthetic artifacts also
  carry a warning on every forecast.
- Compute a finite-sample split-conformal absolute-residual radius from calibration
  predictions. Clip reported intervals to physical bounds. Temporal data do not satisfy
  exchangeability automatically; coverage on the held-out period must be inspected,
  and 90% nominal coverage is not guaranteed for a new facility or changing climate.
- R² is undefined for constant targets, so dry-cooling benchmarks report null rather
  than an artificial perfect score. The R² > 0.80 / MAE < 0.05 target is recorded as
  a result, never used to manufacture or relabel accuracy.
- Joblib models are local trusted artifacts; loading untrusted pickle files is outside
  the supported workflow. Model format version is checked on reload.

## 2026-10-07 — Missingness and grounding design

- Mask only observed target-station records during PDSI <= -2 drought windows, at 10%,
  25%, and 40%. At least 20 seeded replicates are required. Both filling methods use
  the same mask within each replicate to make the comparison fair.
- Spatial filling tries adjacent stations in great-circle distance order at the same
  timestamp, skipping missing donors. It preserves the target's surviving observations.
  A failed spatial fill is reported, not silently replaced by temporal filling.
- Linear filling uses time interpolation, then fills boundary gaps. This reconstructs
  historical gaps and uses later observations; it is not an online forecasting method.
- Evaluate forecasts against the complete target-series baseline over all drought
  records. Store variance in MGD², empirical 5th/95th percentiles, ±0.05 MGD coverage,
  and a stability flag requiring >=90% tolerance coverage and every drought record's
  central band to fit inside the tolerance. These bands quantify missingness sensitivity,
  not measurement uncertainty or predictive confidence against observed targets.
- Permit input is JSONL with explicit sections, source URLs, and HUC or coordinate
  scope. Chunks retain exact character offsets and citation metadata. TF-IDF vectors
  use FAISS cosine ranking. Geographic filtering happens before counting top-k results.
- Narratives are deterministic and extractive. They format the previously calculated
  model output and quote permit excerpts verbatim, without calculating cap exceedances
or interpreting compliance. Empty retrieval and example documents have distinct warnings.

## 2026-10-07 — Live-source checks and application wiring

- Public read-only USGS requests returned HTTP 200 for HUC-prefix CQL filtering and
  daily streamflow. The actual monitoring-location property is `id`, not the historical
  documentation's `monitoring_location_id`. Corrected the client and fixtures.
- Current daily USGS records use scalar `approval_status`; older documentation used
  list `approvals_status`. Preserve both, plus scalar/list qualifiers.
- Limit site discovery to the USGS agency, and allow explicit station selection in
  the HUC query to avoid fetching irrelevant monitoring sites. The ingestion CLI uses
  a required representative flow station and optional additional stations.
- A live NOAA GSOD request for July 1–2, 2024 returned HTTP 200, native Fahrenheit
  TEMP/DEWP fields and precipitation attributes. Conversion assumptions were confirmed.
- NOAA's old nClimDiv directory now redirects (301) to the `monitoring-content` monthly
  current directory. Updated the canonical URL; the CLI also follows redirects.
- Regression/missingness implementation and tests committed as `151326e`.
- Ingestion builds daily aligned observations and monthly median feature snapshots.
  Preserve period, station identifiers, climate division, and record counts. Forecasts
  use historical monthly conditions, not an asserted forecast of future weather.
- The API returns 503 when model or environmental artifacts are absent, and 422 for
  invalid inputs, unsupported months/locations, or absent cooling-type models.
  Missing permits produce an explicit grounding warning and empty citations.
- Coordinate requests select the nearest configured representative station within
  50 km and label that approximation. This is not a polygon-based HUC delineation.
  Supplying an authoritative HUC is preferable near watershed boundaries.
- Model resources load once at application startup. Training does not run in request
  handlers. Forecast requests perform local inference/retrieval without external calls.
- Demo artifacts live in a separate `data/processed/demo` directory, carry synthetic
  labels, and require explicit API data-directory selection. Demo permits are fictional
  and visibly marked; no fabricated EPA citation is used as evidence.
- Added tests for bad requests, unconfigured startup, coordinate resolution, absent
  grounding, source counts, model serialization, training-only imputation, clipping,
  groundwater-depth gap filling, and deliberately unstable spatial donors.
- Added a small typed TypeScript fetch client and CI configuration. CI files are local
  changes; GitHub Actions has not run because no push has been requested.

## 2026-10-07 — Validation and corrections

- First complete suite: 47 passed and three temp-fixture setup errors. The sandbox
  could not enumerate pytest's pre-existing shared temp directory. Set pytest's base
  temp directory to the ignored workspace `.pytest-tmp`, avoiding that external path.
- Rerun: 49 passed, one model-reload test failed. The clipping test had replaced the
  sklearn Pipeline's dynamic `predict` descriptor; monkeypatch restoration stored a
  bound method in the shared fixture, making that *test-mutated* object unpicklable.
  Replaced the model's estimator temporarily instead. Actual demo artifacts had not
  been mutated and loaded normally. Subsequent suite: **50 passed**.
- One upstream Starlette warning remains: its latest TestClient deprecates httpx in
  favor of httpx2. Current tests work with the declared httpx dependency. The warning
  is recorded rather than suppressed.
- `ruff check src tests scripts` and `npm run typecheck` passed. Installed TypeScript
  with an npm lockfile and disabled package install scripts.
- Offline `demo` command completed, writing synthetic training, model, environmental
  snapshots, station matrices, benchmarks, and fictional permit index.
- A two-day live ingestion smoke run completed against USGS + NOAA: two streamflow
  records, two GSOD records, one monthly PDSI value, and one environmental snapshot.
  Observed source period: 2024-07-01 through 2024-07-02. Saved only to ignored
  `data/raw/live-smoke` and `data/processed/live-smoke` directories.
- Verified USGS-01646500 actually belongs to HUC12 `020700081005`, hence HUC8
  `02070008`. The demonstration HUC is a synthetic label and is not asserted to be
  that station's real catchment. The smoke test's NOAA division `4401` checks parsing;
  it is not a verified geographic division assignment for the facility or gauge.
- Verified current NOAA PDSI filename: `climdiv-pdsidv-v1.0.0-20260904`.
- Corrected monthly flow record counts to avoid pandas index-alignment shifts.
- Moved geographic distance arithmetic to `src/geography.py` so ingestion does not
  import the text-grounding/vector-store layer.
- Coordinate-scoped permit retrieval now requires actual request coordinates. A
  HUC-only forecast must not use the gauge's coordinates as the facility's location
  to infer the applicability of a narrowly scoped permit. Added a regression test.
- Notebook source now contains temporal benchmark tables, 50-repeat drought masking,
  tolerance plots, and separate toy groundwater reconstruction in meters. It clearly
  labels synthetic inputs, exposes paths for observed inputs, and saves research outputs.

### Outstanding verification at the previous checkpoint

- Execute the notebook, inspect exported plots, and record the sensitivity results.
- Rerun the suite for the coordinate-permit correction and finish focused commits.
- Field accuracy and actual permit applicability remain unvalidated until measured
  facility labels, verified local station mappings, and real permit sections are supplied.

## 2026-10-07 — Final local verification

- API, CLI, and TypeScript client committed as `66230dc`. This brings the implementation
  to six focused local commits since the README-only starting point.
- Final suite after the coordinate-permit correction: **51 passed**. Ruff lint,
  Ruff formatting, and TypeScript type checking passed. No warnings were suppressed.
- Notebook runner initially tried to create the user's `.ipython` directory and hit
  the sandbox's write boundary. Configured workspace-local IPython/Jupyter/Matplotlib
  runtime directories and the virtual environment's kernel catalog instead. The runner
  now completes without installing a global Jupyter kernel or modifying user settings.
- Executed the full notebook with a real local kernel. All cells completed; exported
  tables and two PNG figures were inspected. Generated artifacts stay out of commits.
- Synthetic selected-model test metrics: cooling tower R² 0.99808 / MAE 0.003668 MGD;
  direct evaporative R² 0.99728 / MAE 0.003191 MGD. Dry-cooling R² is undefined.
- Nominal 90% prediction intervals achieved 88.29% and 87.99% coverage for the two
  evaporative models on the held-out synthetic sample. This shortfall is documented
  explicitly; no guaranteed 90% confidence claim is made.
- The 50-replicate missingness experiment produced six stable synthetic cases: all
  perturbations within ±0.05 MGD, with mean prediction variance from 3.295e-9 to
  4.092e-8 MGD². Strong synthetic neighbor correlation limits what can be inferred.
- Groundwater toy reconstruction retained meters and had separate reconstruction errors.
- Detailed result tables, reproducible commands, limitations, and next field measurements
  are recorded in `docs/validation-results.md`. Usage and data schemas are documented
  in the README and `docs/data-contracts.md`.
- No GitHub access was required for local implementation or commits. No remote push,
  pull request, deployment, or account changes were performed.
