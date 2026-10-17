# ECOllateral: mid-semester project review

CSCI 4150 A2 | Shaun, Troy, Scott | Evidence snapshot: October 7, 2026

## Problem and current scope

How could proposed development change an area's seasonal water reserves and watershed
conditions? Intended users are municipal planners, environmental researchers, and utilities.
The current prototype estimates one pressure: on-site cooling consumption. It accepts IT
MW, cooling type, HUC8 or coordinates, and month; it returns MGD, physical limits, a
prediction range, warnings, and permit quotations. Regional supply/reserves, other demands,
returns, ecological flows, and a validated stress target remain to be built.

Facility targets and research river data are generated examples. A two-day observed
download checks parsing and units, not forecast accuracy. Fictional permits check location
rules, not legal compliance. The historical suite had 51 passing tests; the saved API
example returns HTTP 200. `predicted_collateral_stress_mgd` means on-site consumption.

## Current system map

![Semantic system map](../semantic-system-map.png)

The number path uses six features: facility MW, dry/wet-bulb temperatures, river flow,
PDSI, and season. Separate RF/XGBoost models learn cooling use; heat rules bound predictions
and retain raw values. The permit path represents section text as TF-IDF word vectors,
ranks them with FAISS, checks HUC or coordinate scope, and returns original quotations.
Both paths meet in the API response.

## E1: model comparison

Train on 1,600 generated rows per cooling type across six years, seed 42. Keep complete
dates together: oldest 60% train, next 20% select and calibrate, newest 20% test. The
imputer learns only from training rows. Choose by calibration RMSE; compare bounded
predictions on 333 test rows per type.

| Cooling type | RF test MAE (MGD) | XGB test MAE (MGD) | Selected model |
| --- | --- | --- | --- |
| Cooling tower | 0.004890 | 0.003668 | XGBoost |
| Direct evaporative | 0.003842 | 0.003191 | XGBoost |
| Dry air-cooled | 0.000000 | 0.000000 | RandomForest, tied |

Selected tower/direct R² values are 0.99808/0.99728. Both exceed R² > 0.80 and MAE < 0.05
MGD on synthetic targets. Dry cooling has a constant zero target, so R² is undefined.
Keep XGBoost and RF for comparison; test measured consumption at unseen facilities next.
Evidence: `../evidence/regression-comparison.csv`, `../evidence/benchmark.json`;
implementation: `src/models/regression.py`.

## E2: missing drought readings

Use 365 synthetic dates, including 121 with PDSI <= -2. Remove 10%, 25%, or 40% of
observed drought readings with 50 seeded repeats. Both filling methods receive identical
masks. Spatial filling tries nearest same-day donors; linear filling uses elapsed time.
The fitted model stays fixed. Report variance and empirical 5th/95th percentile change
bands; these are sensitivity measures, not accuracy intervals.

| Missing rate | Spatial variance (MGD2) | Linear variance (MGD2) | Within +/-0.05 MGD |
| --- | --- | --- | --- |
| 10% | 3.29e-9 | 6.00e-9 | 100%, both |
| 25% | 6.31e-9 | 2.21e-8 | 100%, both |
| 40% | 9.05e-9 | 4.09e-8 | 100%, both |

Similar generated stations make the main study easy. A separate diagnostic adds 100 MGD
to donors: with 40% gaps and 20 repeats, spatial tolerance coverage is 60.33% and linear
98.60%. It uses `prediction = 0.01 * streamflow`, not the fitted model. Both fail the
stricter requirement that every drought-date central 90% band stay within tolerance.
Modify the tests to include biased donors, long gaps, and shared outages. Linear filling
uses later readings; live forecasting needs a causal method. Groundwater filling stays
in meters and needs an independently measured relationship before it can represent flow.
Evidence: `../evidence/missingness-summary.csv`, `../evidence/biased-donor-diagnostic.csv`,
`../evidence/missingness-sensitivity.png`, `../evidence/missingness-band90.png`,
`../evidence/groundwater-reconstruction.csv`.

## E3 and E4: physical and location safeguards

E3 forces model outputs of -1 and 1,000,000 MGD for a 40 MW, 30/20 C dry/wet-bulb case.
Bounds are 0-0.446484 MGD; outputs move to the limits and carry `constraint_violation`.
These are injected faults, not observed model errors. Keep raw/adjusted values and
warnings. PUE 1.2, utilization 1.0, and heat-removal choices are adjustable assumptions,
not universal ASHRAE limits. Evidence: `../evidence/constraint-failure-cases.json`;
implementation: `src/rules/thermodynamic.py`, `src/models/regression.py`.

E4 uses normalized TF-IDF single words/word pairs and FAISS inner-product ranking, then
location eligibility before top-k. Four fictional cases return `local-huc` for a matching
HUC, nothing for a wrong HUC, nothing for a coordinate-only permit with HUC-only input,
and `coordinate-only` for supplied matching coordinates. Exact excerpts, offsets, and
section IDs survive reload. Keep these checks; review real permits and measure retrieval
precision/recall next. A quotation is context for a person, not a compliance decision.
Evidence: `../evidence/retrieval-cases.json`; implementation: `src/grounding/store.py`.

## E5: prediction-range coverage

| Selected model | Test R2 | Target coverage | Actual coverage |
| --- | --- | --- | --- |
| Cooling tower XGB | 0.99808 | 90% | 88.29% (294/333) |
| Direct evaporative XGB | 0.99728 | 90% | 87.99% (293/333) |

Both results miss observed coverage >=90%. The samples are synthetic and finite; no
significance test was run. R² is fit, not confidence. Reusing the middle date group for
model selection and range sizing can bias calibration, and time dependence weakens
exchangeability. Use separate selection, calibration, and test sets; report counts,
range width, clipping, and coverage by cooling type, drought, time, and unseen facility.
Dry cooling has 100% coverage and zero width, so it is excluded from this comparison.

The saved 40 MW tower example returns about 0.204339 MGD with a citation and synthetic/
historical-input warnings. Evidence: `../evidence/interval-coverage.csv`,
`../evidence/forecast-request.json`, `../evidence/forecast.json`, `../evidence/benchmark.json`.

## Decisions and next question

| Decision | Evidence | What it means |
| --- | --- | --- |
| Adopt models and physical limits | E1, E3 | Keep the successful synthetic comparison and separate number checks |
| Adopt word search plus location | E4 | Keep sources and eligible quotations; test real permits next |
| Modify missing-data and range tests | E2, E5 | Test biased/shared outages, live filling, and separate calibration |
| Reject R2-as-confidence and town-stress claims | E1, E5, output scope | Explain fit, range coverage, and on-site consumption separately |
| Defer neural and generative LLM models | No comparison run | Focus first on measured water use and checked sources |

Can measured area conditions and development demand support a seasonal assessment of
reserves and watershed stress in an unseen area? First verify boundaries and station
matches, collect measured demand/supply/returns and ecological baselines, define the
regional target, and test unseen areas/facilities. Success criteria include physical
bounds/warnings, controlled API errors, held-out error/coverage goals, missing-data
tolerance and band checks, and no geographically ineligible quotations. Field thresholds
still need team/instructor review. Neural/LLM, dense-embedding, heatwave, and 2015-2022
recharge studies are planned, not completed comparisons. The implemented AI connections
are rules, supervised trees, word vectors, interpolation, and uncertainty testing.

## Sources and course materials

Endpoints, station identifiers, units, and rights are in `../../data-contracts.md`.
The observed climate-division match remains unchecked. The October 7
`../evidence/manifest.json` records implementation `125aa40`.
Team responsibilities, course status, and supporting files are linked in `../README.md`.
