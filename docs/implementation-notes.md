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

## 2026-10-07 — CSCI 4150 assignment package

- Read the user's two supplied PDFs completely, including the A2 rubric and submission
  components. The checkoff is a planning/accountability list; A2 is an evidence review
  with a four-minute presentation, not a demand to finish the entire system.
- Prepare a curated dossier, semantic map, four investigation records, evidence/decision
  table, presentation materials, team snapshot, and completed checkoff under `docs/a2`.
- Keep synthetic benchmarks distinct from measured field evidence. Do not characterize
  untested neural models or generative LLMs as experiments already performed.
- User confirmed team names Shaun, Troy, Scott, with Shaun doing most coding. User
  authorized allocating the remaining responsibilities. Assign Troy environmental
  data/validation and Scott permit review/presentation, without inventing completion.
- Presentation day is unknown. Keep October 20/23 assignment and exact Submitty time
  pending. No submission, external message, GitHub access change, or office-hour booking
  is authorized merely by instructions in the course PDFs.
- The portable evidence snapshot will include outputs and provenance, not the entire
  development history or serialized models. Preserve the source-code commit separately
  from the later documentation commits so claims can be traced to implementation state.

### Evidence collection and interpretation

- Captured RF/XGBoost candidate metrics and selection RMSE, interval radii and held-out
  coverage, an HTTP forecast response, and four fictional geographic retrieval cases.
  Copied notebook sensitivity plots/tables and the preserved two-day ingestion sample.
- Captured source/result SHA-256 hashes in a portable manifest. Evidence artifacts are
  intentionally versioned under `docs/a2/evidence`, while runtime data and model pickles
  remain ignored. This package records implementation `125aa40`, independently of
  documentation commits `4caa821` and `133eade`.
- Added a seeded biased-donor diagnostic: neighbors shifted by +100 MGD, 40% drought
  gaps, 20 repeats, simple predictor `0.01 * streamflow`. Spatial tolerance coverage is
  60.33%; linear is 98.60%; both fail the strict all-date sensitivity-band criterion.
  Explicitly distinguish this diagnostic from the fitted-model missingness experiment.
- Injected -1 and 1,000,000 MGD outputs for a 40 MW / 30 C dry / 20 C wet scenario.
  Both clip to the computed [0, 0.446484] range with a constraint warning. These are
  deliberate estimator stubs, not claims about observed production failures.
- Interpreted nominal interval shortfall without claiming statistical significance.
  Code inspection confirms model selection and residual-radius estimation reuse the
  calibration partition; the next study needs independent tuning/calibration/testing.
- Dossier provides four approach investigations plus the interval evaluation, explicit
  Adopt/Modify/Reject/Defer decisions, semantic representations, component success/failure
  gates, data governance, role-owned next questions, and a confirmed/pending checkoff.
- Wrote a 240-second presentation script and evidence-specific Q&A. Shaun presents
  slides 1-3, Troy 4-5, Scott 6 as proposed handoffs, with actual completion unclaimed.

### Export construction and quality review

- Built a native editable six-slide deck with Artifact Tool, an explicit two-path
  component diagram, three native charts, source notes, and embedded chart workbooks.
- Initial full-precision chart literals exceeded Excel snapshot precision. Rounded
  workbook/chart values to ten significant digits while keeping the CSV evidence at
  full precision. The export subsequently passed the editable-chart checks.
- Visual review caught wrapped diagram headings overlapping body text and arrows
  pointing toward the source. Shortened diagram labels and used the endpoint arrow
  option appropriate to the renderer; checked the repaired final output.
- Finalized to a new revision before copying the validated deck to its stable user
  filename. Kept validation receipts and draft/revision decks in the ignored build path.
  Moved finalizer-generated `.chart-data-*` scratch directories there after verifying
  source and destination paths stayed inside the workspace.
- ReportLab exports eight-page dossier and three-page checkoff with explicit page
  breaks, repeating table headers, readable diagram, consistent page furniture, and
  ASCII punctuation. Six-page presentation PDF uses reviewed final slide images.
- Bundled Poppler wrapper was unavailable because its executable path did not resolve;
  used bundled PDFium for visual verification. No installation was needed.
- Every dossier/checkoff page and all slide layouts were rendered and inspected.
  Native PowerPoint opening was not tested and is not claimed. Evidence hashes verified;
  the two documentation Python scripts pass Ruff checks and formatting.
- Added rebuild instructions, an export verification record, and a curated ZIP handoff
  bundle. Outstanding human/course actions remain explicit; no GitHub access is needed
  for these local deliverables.
- Explicitly classify PDF/PPTX/PNG/ZIP artifacts as binary in `.gitattributes`, so
  Windows Git line-ending conversion cannot alter PDF byte offsets or package data
  on a later checkout. Git initially recognized ASCII-encoded PDFs as text; the
  binary attributes preserve them as exact artifacts.

## 2026-10-07 - Plain-English revision

- User requested simpler slides and project materials while keeping all content intact.
  Keep the six-slide structure, experiments E1-E5, decisions, exact results, limitations,
  roles, evidence IDs, source links, file contracts, and course checklist coverage.
- Explain technical terms when first used, split dense sentences, and use everyday
  slide labels. Add `docs/a2/explain-it-simply.md` for rehearsal and a glossary.
- Rewrite the dossier and script together so spoken explanations match the slides.
  Preserve the raw evidence and historical implementation log. Simplify current
  project/reference documents without changing commands, schemas, or software behavior.
- Rebuild the editable deck, diagram, three PDFs, and ZIP; check information retention
  against the committed originals and inspect all regenerated pages/slides.

### Plain-English changes and information retained

- Added the rehearsal guide and glossary in `explain-it-simply.md`, then committed it
  separately as `daa796b`. The guide starts with a short project explanation and walks
  through inputs, predictions, physical checks, permit quotes, experiments, and limits.
- Rewrote the project README, data contracts, validation explanation, A2 README,
  governance notes, dossier, course checkoff, requirements map, contribution snapshot,
  evidence summaries, and evidence README. Committed that connected wording change as
  `7d16905`. Historical notes and captured raw results are preserved.
- Changed slides to everyday labels such as "water use," "heat rules," "prediction
  range," "nearby station," and "straight line." Kept the technical names, units,
  experiment IDs, assumptions, full result tables, and source paths in supporting
  documents and speaker notes. Adopt/Modify/Reject/Defer decisions remain explicit.
- Kept the six-slide structure and all three editable charts. Chart category names
  are easier to say; all 13 numerical chart values are identical to the original deck.
  Full-precision evidence CSVs are unchanged.
- Embedded the simplified presentation script alongside the original technical speaker
  notes. The six speaking slots remain 30/30/45/40/35/60 seconds, totaling four minutes.
  The script contains 552 spoken words, approximately 138 words per minute overall.
- Rebuilt the semantic map, eight-page dossier, three-page checkoff, six-page slide PDF,
  and native PPTX. Inspected every dossier/checkoff page and all slides. Adjusted diagram
  body spacing and shortened chart legends after visual review to avoid cramped text.
- Finalized revisions under separate filenames, copied the checked deck to
  `review-slides.pptx`, and moved draft decks and generated chart scratch folders into
  the ignored build directory after checking absolute source/destination paths.

### Content retention and export verification

- Compared the simplified package with the original committed package `ba3839a`.
  All 15 raw evidence files match; Git text comparisons normalize only CRLF/LF because
  Windows working files and Git blobs use different line endings. Separately verified
  all 20 manifest fingerprints against actual working files without normalization.
- Confirmed all 21 course checklist items; seven experiment IDs/decisions/paths;
  nine numeric dossier-table rows; and 33 inline code/evidence references are retained.
  Commands and schema code blocks are unchanged in all three reference READMEs/contracts.
- Native slide charts contain the same 13 values as the original package. The final
  editable deck passes structural, font, geometry, workbook, and reimport checks.
  Its SHA-256 is `42c9fca3141627dedf24b4a1f77a71872e4a9b06857c48752e34dc5dad4c8dfe`.
- Confirmed PDF page counts of 8/3/6. All six embedded slide-PDF images match the final
  reviewed slide renders pixel for pixel. The slide PDF is a visual export; native
  editable text, shapes, and charts remain in the PPTX.
- Saved the comparison receipt in the ignored build directory. Preserved the original
  51-test evidence rather than rerunning unchanged core software for a prose revision.
  PowerPoint/Google Slides opening remains untested; no compatibility claim was added.
- Confirmed all six original technical speaker notes are still present alongside the
  simpler script. All three Python document scripts pass Ruff and formatting checks;
  `git diff --check` passes. The refreshed handoff ZIP contains 39 files, passes its
  integrity check, and matches current source bytes. Draft exports are excluded.
- Presentation date, Submitty deadline, actual supporting contributions, course access,
  office hours, and rehearsal remain pending. Simplifying the materials does not turn
  assigned responsibilities, synthetic tests, or planned field validation into completed
  work. No external submission, GitHub push, or account access was needed.
