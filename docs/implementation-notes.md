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
  authorized by Shaun. No push or deployment is requested.
- First commit: package metadata, Make commands, importable modules, ignored runtime
  artifacts, and development instructions.
- The Microsoft Store Python launcher was inaccessible in the local environment. Inspect
  a Python installation before choosing a working local environment.

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
- Environment: created `.venv` using Python 3.12. Network-restricted
  dependency installation failed with Windows socket error 10013; a
  dependency-download retry succeeded. This did not require GitHub access.
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

- First complete suite: 47 passed and three temp-fixture setup errors. The environment
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
- Notebook runner initially tried to create the existing `.ipython` directory and hit
  a filesystem write restriction. Configured workspace-local IPython/Jupyter/Matplotlib
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

- Read the existing two supplied PDFs completely, including the A2 rubric and submission
  components. The checkoff is a planning/accountability list; A2 is an evidence review
  with a four-minute presentation, not a demand to finish the entire system.
- Prepare a curated dossier, semantic map, four investigation records, evidence/decision
  table, presentation materials, team snapshot, and completed checkoff under `docs/a2`.
- Keep synthetic benchmarks distinct from measured field evidence. Do not characterize
  untested neural models or generative LLMs as experiments already performed.
- Shaun confirmed team names Shaun, Troy, Scott, with Shaun doing most coding. User
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

- Built a native editable six-slide deck with an explicit two-path
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
- The Poppler wrapper was unavailable because its executable path did not resolve;
  used PDFium for visual verification. No installation was needed.
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

- Requested simpler slides and project materials while keeping all content intact.
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

## 2026-10-08 - Editorial design for the review slides

- Supplied an exact visual system for the review PowerPoint: off-white/white
  canvas, #111827 primary text, #6B7280 metadata, a #9382FF glow with 45% center opacity,
  uppercase editorial serif titles, thin title bars, clean sans-serif body text,
  stat callouts, split layouts, and at least 40% negative space.
- Applied the Presentations workflow to the existing six-slide content. Verified local
  Georgia and Arial font files before choosing Georgia for headings and Arial for body,
  charts, and metadata. Declared both font families in the export validation policy.
- Kept the experiment order, three editable charts, precise chart values, full technical
  speaker notes, simpler spoken script, course caveats, and synthetic-data disclosures.
  Replaced filled diagram cards with editable text, fine rules, and light connectors.
- Added native editable radial-gradient ellipses rather than raster decorative artwork.
  The final decision slide uses a softly shaded sphere and thin orbit as decoration.
  Decorative geometry does not represent a measured result or experimental evidence.
- The draft passed structural, heading, two-font, chart-workbook, and reimport checks.
- Inspected all six first-draft slide renders. Reduced the heading glow height so
  chart backgrounds do not cut across its edge. Repositioned the final slide's team
  responsibilities to remove an overlap with the next research question.
- Detected an Office owner file from the open PowerPoint. Preserve that temporary
  file, ignore Office owner files in Git, and exclude them from the handoff ZIP.
  This avoids packaging the existing application session metadata.

### Final editorial export and content checks

- Softened chart bars to #B8ADF3 rather than the stronger glow-center color, with
  #D1D5DB comparison/goal bars. All results remain readable against #F9FAFB.
- Re-rendered all six finalized layouts and reviewed the charts, serif title wraps,
  model-selection explanation, source footers, interval warning, role labels, and
  final question. The sphere remains a native editable decorative shape.
- Measured unused space conservatively by subtracting the union of complete foreground
  text/chart/illustration rectangles from the 1280x720 canvas. Excluded only background
  glows and invisible connector anchors. Percentages are 48.14 / 44.69 / 41.67 /
  41.62 / 40.12 / 47.43 for slides 1-6, so every slide exceeds the requested 40%.
- Compared all six original speaker-note parts with `4f4ae28`; every original note
  text is retained. All 13 chart values match the earlier package, and all 20 recorded
  manifest fingerprints still match source/result bytes. Raw evidence is untouched.
- Repeated the existing content-retention checks: 15 raw evidence files, 21 checklist
  items, seven evidence IDs/decisions/paths, nine numeric dossier rows, 33 code/evidence
  references, and all three sets of command/schema blocks remain intact.
- Export validation passed structure, slide dimensions/count, heading placement,
  Georgia/Arial fonts, native charts and embedded workbook snapshots, and first-party
  reimport. Final deck SHA-256:
  `0a8b06ad977d9bb627130779d834ce7bcfb55709a12ee59f1b915265c6061329`.
- Refreshed only the six-page slide PDF from the reviewed images. All six embedded
  PDF images match the final renders pixel for pixel. The dossier/checkoff PDFs and
  other evidence are unchanged. Export receipts remain in the ignored build directory.
- Copied the validated bytes to the stable `review-slides.pptx` filename successfully
  despite an existing Office owner file. Reopening a previously open deck is necessary
  to view the updated disk version. No application-session state was changed.
- Refreshed the 39-file handoff ZIP, verified its integrity, and checked every archived
  file against current workspace bytes. Temporary Office owner files and draft decks
  are excluded. The packaging script passes Ruff and formatting; `git diff --check`
  passes. This design-only task needs no core software test rerun or GitHub access.

## 2026-10-08 - Restore the regional ecosystem purpose

- The presentation review corrected the data-center focus using a fuller project
  summary. The intended project is Environmental Impact Assessment and Regional Ecosystem
  Forecasting: proposed development's effects on municipal water reserves and watershed
  conditions across seasons, for planning boards, researchers, and utility operators.
- The earlier review incorrectly elevated the implemented cooling demo into the project's
  overarching purpose. Correct the current documents and slides while retaining historical
  implementation notes and raw evidence. Cooling is one development-pressure component.
- Added `docs/project-scope.md` with the regional question, current-versus-planned matrix,
  area-assessment steps, target/validation requirements, and team ownership. The current
  API is not a regional ecosystem assessment and its field must not be relabeled as one.
- Reframed README, dossier, rehearsal guide, script/Q&A, checkoff, requirement map, team
  assignments, governance, evidence explanations, contracts, and validation introduction.
  Exact API/schema commands, experiment values, evidence paths, and source metadata remain.
- Context contains planned/anticipated items despite its statement that three paradigms
  were benchmarked. Do not invent an LLM experiment, historical heatwave study, dense
  embeddings, HUC polygon implementation, EIA/EPA ingestion, or 2015-2022 recharge tests.
  The current search is TF-IDF/FAISS; groundwater depth in meters is not recharge.
- Regional validation requires observed supply/reserves, other demands, return flows,
  ecological flow needs, checked area boundaries, regional labels, and unseen-area tests.
  Preserve component checks and uncertainty limitations as evidence of reusable methods.
- Supporting responsibilities follow the supplied breakdown: Troy environmental acquisition,
  area/drought interpretation and grounding; Scott safety/interface evaluation, failure
  analysis, regional evidence and slides. Shaun remains the main coding contributor.
  Assignments are not claims of completed contributions.
- Include the new scope document as the fourth project reference in the handoff ZIP.
  Preserve the existing editorial slide design while correcting the purpose and next question.

### Regional storyline and export construction

- Slide 1 now opens "Ecosystem impacts across an area" for municipal planners,
  researchers, and utilities, with separate regional-goal/current-prototype columns.
  The cooling model is explicitly one development-pressure case study.
- Slide 2 labels the existing API and number/document paths as current components;
  regional reserve/stress integration is planned. Slide 3 retains the exact model
  comparisons as one pressure-component test rather than a regional stress benchmark.
- Slides 4-5 keep missingness and range results unchanged. Slide 6 asks about seasonal
  reserve and watershed impacts in an unseen area and prioritizes area balances,
  ecological baselines, and regional tests. Component rules remain distinct from
  ecological/utility thresholds. Sources and raw result references remain in the notes.
- Kept Georgia/Arial, #F9FAFB canvas, charcoal text, muted captions, native lavender
  glows, thin title bars, three editable charts, and the native decorative sphere.
  Rebalanced the cover's two lines after visual review. Corrected spoken purpose and
  final question while retaining the original component-method notes on all six slides.
- Updated the standalone map with the regional goal above the current component paths
  and a clear statement that area balances, ecological thresholds, and recharge inference
  remain planned. Dossier/checkoff exports remain eight/three pages; slides remain six.
- Current script is 565 words over 240 seconds (141.25 words/minute overall), with
  77/79/103/96/84/126 words in the six timing slots. Regional framing Q&A distinguishes
  intended assessment, current cooling evidence, and proposed studies in the project context.
- Changed only the package description in pyproject.toml to match the project identity.
  Parsed both old/new TOML and confirmed every other metadata/dependency field is identical.
  No API behavior, model logic, or data schema changed.

### A2 assignment audit and explicit slide labels

- Reread all three pages of the supplied A2 brief and the project checkoff PDF.
  The seven required presentation topics are problem/users, current semantic map,
  at least three investigations, concrete evidence, consequential failure/limitation,
  evidence-supported decisions, and the most important next question. The five
  submission components are dossier, map, evidence/decision summary, slides, and
  one-line teammate statements. Course instructions do not authorize external submission.
- Added `docs/a2/slide-coverage.md` with a seven-item requirement matrix, exact visible
  headings by slide, the six rubric categories, timing, five deliverables, and pending
  human checks. The matrix documents coverage and makes no prediction about a grade.
- Made slide 2 explain meaning representation directly: observation units/dates,
  six features, cooling-use target, RF/XGBoost, PUE/heat rules, original document words,
  TF-IDF word vectors, source/section/location metadata, geographic filtering, quotations.
  Explain how learned numbers, symbolic checks, and retrieved context work together.
- Added concrete E3 fault-injection clipping range and E4 four-case location result
  on slide 2; E1/E2/E5 each retain their own native chart and evidence source footer.
  E3/E4 are extra investigations, not substitutes for the three main chart slides.
- Split slide 6 into four explicit decisions with reasons: E1 lower XGBoost error and
  E3/E4 passing safeguards support Adopt; E2 biased donors and E5 observed coverage
  shortfall support Modify; fit cannot stand for confidence and cooling use cannot
  stand for area impact; absent regional labels/LLM benchmarks support Defer.
- Requested visible names for assignment sections. Headings now say Problem &
  Users, Semantic Map, Experiment E1/E2/E5, and Decisions & Next Question. The failure
  and reliability issue are explicitly labeled in slides 4/5; slides 2-5 identify their
  sources with an Evidence footer. IDs match the dossier and evidence summary.
- Retained regional ecosystem purpose and distinguish current component evidence from
  planned area assessment. Keep actual results, chart values, raw evidence, and original
  component-method notes unchanged; do not invent regional validation or LLM experiments.
- Updated the timed talk and speaker notes. Current spoken counts are 77/77/103/96/84/135,
  totaling 572 words over 240 seconds (143 words/minute). The 30/30/45/40/35/60-second
  allocation follows 1 minute problem/map, 2 minutes experiments/failures, 1 minute
  decisions/next question; allow 2 minutes for questions and rehearse to verify pacing.
- Actual teammate contributions, presentation date/deadline, studio links, instructor
  access, office hours, and all three members' understanding still require human/course
  confirmation. The local package is prepared evidence, not proof of those actions.

### Remove the circular gradients

- Requested removing the purple circle gradient decoration. This
  supersedes the earlier requested glow/abstract-sphere treatment. Removed every
  background radial glow, the final slide's shaded sphere, and its thin orbit.
- Keep the off-white canvas, charcoal type, serif headings, thin rules, open layout,
  three editable charts, explicit A2 labels, and full evidence. Muted chart colors
  remain comparison encodings; no circular-gradient decoration remains.
- Update the reproducible builder and package description so rebuilding does not
  bring the removed decoration back. Re-export and visually inspect the final deck
  before refreshing the matching slide PDF and prepared handoff ZIP.

### Final regional/A2 export verification

- Reviewed all six final clean-background slide renders at full size, including
  serif title wrapping, explicit assignment names, Evidence footers, semantic paths,
  failures, four decision rows, proposed roles, and the unseen-area next question.
  Rechecked the final checkoff pages after regional roadmap/role updates; dossier,
  checkoff, and slides remain eight/three/six pages. All dossier pages were reviewed.
- Finalizer passed slide dimensions/count, structure, heading fit, Georgia/Arial,
  three native charts, embedded literal workbooks, and file reimport.
  Final deck SHA-256:
  `4ba13652d80b698ce942fd51dfa68a8e1b3fe251ca8b1e93111a98d7afe9fd54`.
- Final foreground-rectangle space check gives 42.92 / 44.69 / 41.67 / 41.62 /
  40.12 / 54.54 percent unused space. Every slide meets the requested minimum 40%.
  No slide retains gradient-fill shapes or decorative ellipses.
- Refreshed the stable PowerPoint and matching slide PDF; all six PDF images match
  the reviewed slide renders pixel for pixel. Preserve the open Office owner file;
  an already-open PowerPoint needs reopening to display the updated disk version.
- Content comparisons pass for 15 raw evidence files, 20 recorded fingerprints,
  three command/schema-block groups, 33 original dossier references, nine numeric
  dossier-table rows, 21 checkoff items, seven evidence IDs/decisions/paths, 13 native
  chart values, and all six original component-method notes. Core behavior is unchanged.
- Ruff and formatting pass for all three Python capture/export/packaging scripts.
  No core-suite rerun is needed for this documentation/design revision; its historical
  51-test result remains intact. Native PowerPoint/Google Slides opening is untested.
- Move temporary drafts and chart-data folders into the ignored workspace build area.
  Refresh the 41-file ZIP after notes updates, check its integrity and each entry against
  current workspace bytes, and exclude Office owner files and draft decks. No external
  submission, GitHub push, message, or access change is part of this local revision.

## 2026-10-08 - Make the review easier to explain

- Requested another pass to remove unnecessary complex words and make the whole
  deck easier to explain. Preserve the regional ecosystem purpose, six slides, clean
  background, editable charts/map, exact results, and explicit A2 requirement labels.
- Replace technical language in visible text: calibration becomes setting ranges;
  metadata becomes source/location details; vectors become words as numbers; imputation
  becomes filling missing readings; biased neighbors become neighbors reading too high;
  regional labels become real area measurements; area balances become area water totals.
- Keep official model names, units, evidence filenames, experiment IDs, and Semantic Map,
  Evidence, Failure / Reliability Issue, Adopt/Modify/Reject/Defer labels so course
  requirements and evidence remain easy to find. Add plain explanations of Reject/Defer.
- Simplify the timed talk and Q&A, including definitions of watershed and semantic map.
  The diagram's two paths still explain learned numeric targets, physical checks, word
  representations, source details, geographic filtering, and original permit quotations.
- Present the short talk first in PowerPoint notes. Retain the original full component
  methods under Extra details for questions, including setup, exact counts, source paths,
  synthetic-data limits, calibration reuse, diagnostic formula, and engineering assumptions.
- Add one short takeaway per slide to the rehearsal guide. Update the coverage matrix
  to match the new exact headings rather than leaving stale slide names in the package.
- Planned verification: render every slide, review wrapping/readability, check source
  values and notes are retained, confirm all seven A2 requirements, refresh the matching
  PDF/ZIP, and commit sources and verified exports separately. No core code changes.

### Semantic-map arrow adjustment

- The review found that slide 2's arrows should move slightly left and down. Offset
  the native connectors' invisible anchors by -8px horizontally and +10px vertically.
  Text boxes and diagram columns stay in their existing positions. Eight horizontal
  arrows and the vertical quote/result arrow remain editable and point the same way.
- First plain-language render preserved the overall layout but the longer failure
  caption wrapped to three lines. Shorten it to "FAILURE: high readings" and retain
  the explanation that neighboring stations read too high in the script and takeaway.
- Re-render the adjusted map and shortened caption, then inspect all final slides.
  The precise arrow offset, final counts, content checks, and package receipt will
  be recorded with the export verification below.

### Preserve the open deck and provide the revised version

- PowerPoint now holds a write lock on `review-slides.pptx`; the attempted stable-file
  copy failed. Do not close the existing app or change their open document. Saved the
  validated revised bytes as `review-slides-simplified.pptx` alongside the preserved old deck.
- Update the package README, requirements/coverage maps, builder default, and ZIP
  required-file list to identify the simplified deck as current. Exclude the preserved
  old deck from the ZIP so the handoff contains one current presentation, not two versions.
- The first post-copy audit still referenced the old deck after the copy failed.
  Correct the private audit paths to the actual simplified file and rerun them before
  relying on the deck fingerprint, notes, or geometry results. The PDF uses the revised
  reviewed renders. No failed copy is treated as evidence of a successful deck update.

### Final plain-language export checks

- Reviewed every first simplified render and the final adjusted semantic map and failure
  slide. The other four final slides retain the same inspected layouts. Removed the
  three-line failure-caption wrap by shortening it, keeping the causal explanation.
- Verified all nine native connector offsets against `1d7b409`: each is -8px/+10px.
  All six required section headings, four Evidence footers, failure/reliability labels,
  four decision categories, and area-focused next question appear in the final PPTX.
- Verified every speaker-notes part begins with the current simple talk, followed by
  Extra details for questions. All six spoken sections match the script. Counts are
  66/69/104/101/89/144 words, 573 total over four minutes (143.25 words/minute).
- Full retention checks pass: 15 raw evidence files, 20 fingerprints, three command/schema
  groups, 33 dossier references, nine numeric table rows, 21 course checklist items,
  seven evidence IDs/decisions/paths, 13 chart values, and six original method-note sections.
- Finalizer passes package structure, slide dimensions/count, heading fit, Georgia/Arial,
  three editable charts and workbooks, and file reimport. Final simplified
  deck fingerprint is `40f38dc135c62cb3cd670b7b4f05b328707659d73aa2a0cf2474891dbd667185`.
  All six matching slide-PDF images agree pixel for pixel with final reviewed renders.
- Conservative remaining space is 42.92/44.70/41.67/41.62/40.12/54.54 percent. No purple
  gradients were reintroduced. All core implementation and raw evidence remain unchanged.
- Updated the packaging script to require the simplified deck and omit the locked old
  deck. It passes Ruff and formatting. Move temporary exports/chart workbooks into the
  ignored build area, then verify the refreshed 41-entry ZIP matches current workspace
  bytes and contains one current deck. Preserve the existing application owner file.
- No GitHub access, core-suite rerun, external submission, or app-session change is needed
  for this wording and layout revision. Native PowerPoint/Google Slides opening remains
  untested; use the new simplified filename to view the current deck.
## October 8, 2026: real measurements and a smaller A2 folder

- Requested clearer slide wording about training on measured data and deletion
  of unnecessary folders/files. Generated water-use examples remain evidence of
  software checks only. Real-data training and separate testing on unseen records
  and areas are next steps; no new model training or regional validation is claimed.
- Update slides 1, 3, and 6 and their spoken notes. Preserve all measured experiment
  numbers, original component methods, A2 headings, diagram-arrow positions, and
  current off-white design without purple circular gradients.
- Preserve the existing edits to the script, including removal of the top timing table.
  Merge the complete simple project guide and glossary into the script. Merge the
  requirements and slide-coverage guides into assignment-coverage.md, keeping the
  seven presentation topics, six rubric categories, five deliverables, source PDF
  page references, and pending course checks.
- Move editable dossier, checkoff, governance, and verification Markdown into
  docs/a2/source/. Move the two document builders and evidence collector into
  scripts/a2/, with rebuild instructions there. Fix active links and source paths.
- Delete the duplicate ZIP and its packaging script, the superseded PowerPoint,
  and the three guides whose content was merged. Retain raw experiment evidence,
  canonical exports, editable sources, and required app dependencies.
- Windows initially blocked removal of the old PowerPoint because it was open.
  Shaun closed it; removal then succeeded. Preserve application owner files and
  do not close applications or touch unrelated user files.
- Next verification: rebuild exports; compare evidence, fingerprints, chart values,
  method notes, and checklist items; inspect final slides/PDF pages; safely remove
  obsolete build drafts and caches. Record actual checks and cleanup counts below.

### Final export, folder cleanup, and portability checks

- Updated slides 1/3/6: generated examples are prototype checks; measured inputs and
  outcomes are needed for training and separate testing on new records/areas. No new
  model or area experiment ran. The current spoken talk is 604 words, about 151 per
  minute over four minutes, so rehearsal remains necessary.
- Reduced the A2 root from 23 files to 11. Merged guides retain the complete glossary,
  walkthrough, numbers, assignment mapping, submission components, and course checks.
  Editable source documents moved to source/; experiment evidence stayed in evidence/.
- Keep portable PDF/evidence scripts and the editable PowerPoint. Removed the
  environment-specific slide builder and replaced its instructions with direct slide
  editing and export steps. Updated active source paths and data-governance references.
- Cleaned obsolete drafts, repeated renders, chart snapshots, assignment-page previews,
  and test/lint caches: 147 files, 13,574,564 bytes. Checked every resolved removal path
  against the workspace; refused recursion through links. Removed only the temporary
  dependency junction itself, preserving its target and all actual installed dependencies.
- Removed exporter labels from document properties and used neutral project theme
  names. Set the correct six-slide/six-note counts and project title. The three native
  charts and their embedded workbooks remain intact. Existing Git history is retained.
- Final presentation passed structural, layout, font, chart/workbook, and reimport checks.
  Metadata changes were finalized and validated before promoting the stable filename.
  Fingerprint: c5b5d7d4b89c92a21632ed1ea3fb5b06ef235c63101ba4bbe099b8f16a8c433b.
- Preserved 15 raw evidence files, 20 fingerprints, nine numeric dossier rows, 21
  checklist items, seven evidence IDs/decisions/paths, 13 chart values, and six original
  component-method notes. Retained 32 active code/evidence references; removed only
  the obsolete slide-builder reference. Project README/data-contract code blocks remain.
- Verified all nine current map connectors equal the last aligned deck, all six notes
  match the current script, required labels/decision categories remain, and 18 local
  Markdown links resolve. No circular gradients were reintroduced. Remaining space by
  conservative rectangle estimates: 42.92/44.70/41.67/41.62/40.12/54.54 percent.
- Rendered/reviewed all final slides and document pages: dossier eight, checkoff three,
  slides six. All six PDF slide images match finalized renders pixel for pixel. The
  Python scripts pass lint/format checks. The current verification guide replaces stale
  ZIP/locked-deck/draft claims; earlier technical history remains in this log.
- No application implementation, experiment outcome, teammate completion, course
  submission, or repository access changed. The prior 51-test capture is retained;
  native PowerPoint/Google Slides opening and real-area forecast accuracy remain unverified.
