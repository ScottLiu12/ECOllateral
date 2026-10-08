# ECOllateral: mid-semester system evidence review

CSCI 4150 A2 | Shaun, Troy, Scott | Evidence snapshot: October 7, 2026

## 1. Problem, users, and current scope

**Primary question:** Can a hybrid system estimate physically plausible on-site cooling water consumption, show its uncertainty, and attach geographically relevant regulatory excerpts to a proposed facility scenario?

The intended users are researchers and infrastructure planners comparing cooling options before a detailed engineering study. A request supplies IT capacity in MW, cooling type, HUC8 watershed, and forecast month. The prototype returns estimated consumption in million US gallons per day (MGD), bounds, a residual-based interval, data-quality warnings, and source quotations.

**Working scope:** public environmental ingestion, unit conversion, monthly scenario features, separate regressors for three cooling types, physical clipping, geographically scoped permit retrieval, a FastAPI endpoint, a typed TypeScript client, and a reproducible missingness notebook. There are 51 passing local tests. The API demonstration loads persisted artifacts and returns HTTP 200 with explicit synthetic-data warnings.

**Evidence boundary:** facility labels and research hydrology are synthetic. Two days of live USGS/NOAA data establish connectivity and parsing, not forecast accuracy. Fictional permit sections establish retrieval mechanics, not compliance. The response field named `predicted_collateral_stress_mgd` currently represents on-site consumption; no municipal supply-demand stress model has been validated.

## Feasible milestones

The implementation milestone is a reproducible local prototype. The A2 milestone is an inspectable map, comparative experiments, consequential limitations, and evidence-driven decisions. Before making field claims, the team needs measured consumption labels, validated station geography, real permit excerpts, and an independent uncertainty evaluation.

This dossier is a curated snapshot. Full implementation details remain in `../implementation-notes.md`, `../data-contracts.md`, and `../validation-results.md`. Portable artifacts in `evidence/` are tied to source hashes in `evidence/manifest.json` and implementation commit `125aa40`.

<!-- pagebreak -->

## 2. System map and semantic representations

![Semantic system map](semantic-system-map.png)

**Meaning enters through different representations.** Numeric features encode capacity, dry/wet bulb temperature, streamflow, PDSI, and seasonal position. The supervised label is consumption in MGD. Trees learn nonlinear feature-to-label relationships. Engineering rules encode an allowed consumption range. Permit meaning is represented by source text, section identifiers, HUC/radius metadata, and normalized TF-IDF vectors.

**Interaction:** the regressor estimates a value; independent rules constrain that value and expose violations. Retrieval ranks lexical matches and applies geographic eligibility before returning top-k quotations. Extractive prose uses those quotations and the numeric result. It performs no LLM arithmetic and issues no legal compliance decision.

Offline training uses distinct dates in chronological 60/20/20 train/calibration/test partitions. Missing flow and PDSI are imputed using training data only. Model selection and residual-radius estimation currently reuse the calibration partition; Section 6 explains why this needs modification.

HUC identity is a semantic join, not a distance measurement. A HUC-only request cannot silently treat a river gauge coordinate as the facility coordinate for a radius-scoped permit. Units remain explicit throughout; groundwater depth in meters is never converted to MGD without a physical model.

<!-- pagebreak -->

## 3. Investigation E1: tabular regression choice

**Hypothesis:** the six features provide enough structure for tree-based models to learn the synthetic cooling response surface. Compare RandomForest and XGBoost separately for each cooling type rather than assuming one model is best everywhere.

**Setup:** 1,600 synthetic observations per cooling type across six years; seed 42; chronological date groups; select the candidate using calibration RMSE and evaluate the selected model on held-out dates. Both candidates receive the same input features and train-only imputation. The benchmark target is R2 > 0.80 and MAE < 0.05 MGD. These are prototype targets, not engineering acceptance criteria.

| Cooling type | RF test MAE (MGD) | XGB test MAE (MGD) | Selected model |
| --- | --- | --- | --- |
| Cooling tower | 0.004890 | 0.003668 | XGBoost |
| Direct evaporative | 0.003842 | 0.003191 | XGBoost |
| Dry air-cooled | 0.000000 | 0.000000 | RandomForest, tied |

The two nonzero-response test sets each contain 333 rows. Selected R2 is 0.99808 for cooling towers and 0.99728 for direct evaporation. Dry air cooling has a constant zero on-site water target, so R2 is undefined and the combined benchmark target is not reported as met for that case.

**Decision: Adopt.** Keep XGBoost for the two evaporative types and RandomForest as a comparative baseline. Preserve per-type model selection. Retain the explicit zero-water boundary for dry air cooling under the stated on-site scope.

**Interpretation limit:** the models learn a constructed label mechanism; high accuracy does not demonstrate accuracy at real facilities or in an unseen watershed. Cooling type is modeled separately, not encoded as a fourth independent comparison. Measured labels and facility-level holdouts are the next evidence gate.

**Inspect:** `evidence/regression-comparison.csv`, `evidence/benchmark.json`; implementation `src/models/regression.py`. Calibration RMSE values are retained so the selection rule is auditable.

<!-- pagebreak -->

## 4. Investigation E2: drought missingness

**Hypothesis:** reconstructing randomly missing drought observations using spatial donors or linear interpolation keeps the fitted forecast within 0.05 MGD of its complete-data prediction.

**Setup:** 365 synthetic dates, 121 drought records defined by PDSI <= -2, removal rates 10%, 25%, and 40%, and 50 repeats per strategy. Spatial filling uses the nearest available same-day station; linear time filling bridges gaps in the target series. The comparison holds the fitted consumption model fixed. Sensitivity bands quantify perturbations from missingness; they are not prediction intervals for future consumption.

| Missing rate | Spatial variance (MGD2) | Linear variance (MGD2) | Within +/-0.05 MGD |
| --- | --- | --- | --- |
| 10% | 3.29e-9 | 6.00e-9 | 100%, both |
| 25% | 6.31e-9 | 2.21e-8 | 100%, both |
| 40% | 9.05e-9 | 4.09e-8 | 100%, both |

**Consequential counterexample:** the correlated synthetic neighbors make the main test easy. An additional diagnostic shifts donor streamflow upward by 100 MGD. At 40% removal and 20 repeats, spatial tolerance coverage falls to 60.33%; linear coverage is 98.60%. This diagnostic uses `prediction = 0.01 * streamflow`, not the fitted ML model. It demonstrates donor-bias exposure, not a measured failure rate of the production regressor. Both fail the strict criterion requiring every drought-date 90% perturbation band to stay within tolerance.

**Decision: Modify.** Keep both methods as research baselines, verify donor hydrologic similarity, and test contiguous drought outages and shared station outages. Linear interpolation may use later observations and is unsuitable for a causal live forecast without a separate causal strategy. Groundwater reconstruction is evaluated separately in meters.

**Inspect:** `evidence/missingness-summary.csv`, `evidence/biased-donor-diagnostic.csv`, `evidence/missingness-sensitivity.png`, `evidence/missingness-band90.png`, and `evidence/groundwater-reconstruction.csv`.

<!-- pagebreak -->

## 5. Investigations E3 and E4: rules and retrieval

### E3: independent physical constraints

**Hypothesis:** a faulty or extrapolating regressor should not silently return impossible consumption. Rules calculate thermal energy and a latent-heat evaporation ceiling from capacity, utilization, PUE, and ambient conditions. A 40 MW scenario with 30 C dry bulb and 20 C wet bulb has a computed range of 0 to 0.446484 MGD under the current assumptions.

Fault injection forces raw predictions of -1 and 1,000,000 MGD. The pipeline clips them to 0 and 0.446484 MGD and includes `constraint_violation`. These values are intentionally injected stubs, not actual fitted-model errors. The test proves the guardrail and warning behavior.

**Decision: Adopt.** Preserve raw predictions, clipping, and visible warnings. PUE 1.2, utilization 1.0, and the heat-removal assumptions remain configurable engineering assumptions. They are not universal ASHRAE bounds or a complete water balance including every facility use.

**Inspect:** `evidence/constraint-failure-cases.json`; `src/rules/thermodynamic.py` and `src/models/regression.py`.

### E4: lexical vectors plus geographic scope

**Hypothesis:** a permit's textual relevance is insufficient unless its location metadata matches the request. Normalized TF-IDF unigram/bigram vectors are searched through FAISS inner product. Geographic eligibility is applied before top-k selection.

Four fictional-corpus cases show: matching HUC returns `local-huc`; wrong HUC returns no section; a HUC-only request excludes a coordinate-only permit; actual matching coordinates include it. Returned text preserves section identifiers and exact excerpts.

**Decision: Adopt.** Keep lexical retrieval, explicit metadata, and extractive quotations as an auditable baseline. Evaluate precision/recall with real, human-reviewed permits before expanding the corpus. TF-IDF is a lexical representation; it does not establish deep semantic understanding or legal applicability.

**Inspect:** `evidence/retrieval-cases.json`, `src/grounding/store.py`, and `src/grounding/generator.py`.

<!-- pagebreak -->

## 6. Failure E5: fit is not uncertainty calibration

**Hypothesis tested:** the nominal 90% residual intervals should achieve approximately their nominal held-out coverage. R2 and coverage measure different properties and must be reported separately.

| Selected model | Test R2 | Nominal coverage | Observed coverage |
| --- | --- | --- | --- |
| Cooling tower XGB | 0.99808 | 90% | 88.29% (294/333) |
| Direct evaporative XGB | 0.99728 | 90% | 87.99% (293/333) |

The observed coverage falls below nominal on these finite synthetic test samples. This does not by itself prove a statistically significant calibration failure, but it fails an observed-coverage >=90% prototype gate. A strong fit score does not justify advertising reliable 90% coverage.

**Code-level limitation:** the same calibration partition selects RF versus XGBoost and sets the residual interval radius. Selection can affect calibration residuals. Chronological environmental data may also violate exchangeability assumptions. We therefore do not claim an independently validated conformal guarantee.

**Decision: Modify.** Separate tuning, interval calibration, and final testing; evaluate coverage by time, drought state, cooling type, and held-out facility. Report sample counts, interval width, and uncertainty around the coverage estimate. Recheck coverage after clipping and outside synthetic label distributions.

**Decision: Reject.** Do not interpret R2 as a confidence probability. Do not present the consumption proxy as a validated municipal stress index. Both interpretations exceed the evidence.

**Inspectable demonstration:** `evidence/forecast-request.json` and `evidence/forecast.json` show a 40 MW tower request returning about 0.204339 MGD with a citation and explicit synthetic/historical-data warnings. This is a functional API demonstration, not independent accuracy evidence.

**Inspect:** `evidence/interval-coverage.csv`, `evidence/benchmark.json`, `src/models/regression.py`. The air-cooled constant-zero case achieves 100% coverage with zero width and is excluded from the substantive interval comparison.

<!-- pagebreak -->

## 7. Evidence-driven decisions and next investigation

| Decision | Evidence | Consequence |
| --- | --- | --- |
| Adopt tree models and physical bounds | E1, E3 | Retain an accurate synthetic baseline with independent numeric safeguards |
| Adopt lexical retrieval with geography | E4 | Preserve quotations and eligibility metadata; review a real corpus next |
| Modify missingness and uncertainty evaluation | E2, E5 | Add biased/shared outages, causal filling, and independent calibration |
| Reject R2-as-confidence and municipal-stress claims | E1, E5, output scope | Label fit, coverage, and on-site consumption separately |
| Defer neural and generative LLM models | No comparative evidence | Spend the next iteration on valid labels and sources |

**Most important next question:** Does the constrained regressor generalize to measured consumption at an unseen facility during drought, with adequate interval coverage? This has greater value than adding a more elaborate model to the same synthetic labels.

**Next evidence plan:** Shaun separates model tuning from interval calibration and establishes a facility holdout protocol. Troy verifies station/HUC/climate-division mappings, obtains an eligible measured-label dataset if available, and evaluates contiguous/shared drought gaps. Scott curates real permit sections with source/scope metadata and a small human-reviewed relevance set. Run the same RF/XGB baselines and report MAE, RMSE, R2, coverage, width, clipping frequency, missing-data flags, and retrieval precision/recall.

**Success/failure gates:** numeric outputs stay in the calculated range and expose clipped values; invalid inputs and missing artifacts produce controlled API errors; benchmark accuracy meets its stated target; observed interval coverage reaches the agreed target on a genuinely held-out evaluation; missingness perturbations meet tolerance without hiding band failures; retrieval never returns an ineligible geography. Real-world thresholds need team/instructor review before deployment claims.

**Connections to class AI concepts:** symbolic rules encode domain knowledge; supervised trees operate on numeric representations; vector-space retrieval maps documents to lexical features; interpolation investigates incomplete observations; uncertainty evaluation tests the reliability of learned outputs. Their interfaces are the central design question. Specific studio names and links were not supplied and remain pending confirmation. No neural or generative LLM experiment is claimed.

<!-- pagebreak -->

## 8. Team, provenance, and submission readiness

**Shaun:** primary coding contributor; leads ingestion, constraints, model/API integration, and the typed client.

**Troy:** assigned environmental provenance, station/geography validation, drought sensitivity review, and evaluation interpretation.

**Scott:** assigned permit-source/scope review, evidence and presentation curation, and coordination of rehearsal and instructor-access checks.

Shaun's coding contribution is confirmed by the user. Troy's and Scott's lines allocate supporting responsibilities; they do not certify completed activity. Each member must confirm their actual contribution before the one-line statements are submitted. Proposed speaking handoff: Shaun slides 1-3, Troy 4-5, Scott 6.

**Data provenance:** USGS continuous observations, NOAA GSOD weather, and NOAA monthly climate-division PDSI supply the ingestion interfaces. The preserved July 1-2, 2024 smoke snapshot uses USGS-01646500 (HUC8 02070008), NOAA station 72403093738, and climate division 4401. The climate-division geographic match is unverified; this snapshot is not the synthetic HUC 02070010 API scenario. NOAA and USGS publish public data; dataset-specific third-party and permit-source rights still require checking. Exact endpoints and official rights references are in `data-governance.md`.

No survey, IRB approval, instructor scraping approval, office-hours booking, GitHub permission change, or course submission has been performed by preparing these materials.

**Ready for review:** dossier, system map, evidence summary table, editable slides and PDF, four-minute script with Q&A, contribution snapshot, and full checkoff mapping. The evidence manifest includes hashes and experiment provenance. `collect_evidence.py` refreshes the evidence from the local project environment; `build_materials.py` and `build_slides.mjs` record export construction.

**Still pending:** assigned presentation date (October 20 or 23, 2026), exact Submitty deadline, instructor/TA repository access, office-hours appointment, rehearsal, actual contribution confirmation, and studio-specific links. The course briefs supply requirements; they do not authorize external messages, uploads, or access changes.

**Repository:** https://github.com/ScottLiu12/ECOllateral. The configured remote is verified locally; collaborator access and publication of the current local snapshot are unverified. No GitHub credentials are needed to create this local package.
