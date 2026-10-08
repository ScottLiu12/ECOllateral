# ECOllateral: regional ecosystem impact assessment

## Purpose and primary question

ECOllateral is an Environmental Impact Assessment and Regional Ecosystem Forecasting
Engine. Its focus is the area affected by development: municipal water reserves,
seasonal water availability, and watershed stability. Municipal planning boards,
environmental researchers, and public utility operators are the intended users.

**Primary question:** Given a proposed development's resource demands, cooling
requirements, and location, how could it affect the surrounding area's municipal
water reserves and watershed conditions across seasons?

Cooling water is one development pressure used to test the current pipeline. It
does not define the whole project, and a facility's consumption is not an ecosystem
health score. Regional outcomes must account for conditions and competing demands
outside an individual facility.

## Goal versus current implementation

| Part | Current evidence | Work still required |
| --- | --- | --- |
| Area and season | HUC8/station metadata, coordinate approximation, monthly environmental snapshots | Verified watershed polygons, utility/service boundaries, and station representativeness |
| Environmental conditions | USGS flow, gauge height, groundwater depth; NOAA weather and PDSI ingestion | Long observed histories, regional quality gates, verified ecological/utility baselines |
| Development pressure | A cooling-water scenario model with adjustable physical limits | Other development demands, independently measured withdrawals and returns, cumulative pressures |
| Regional water impact | No validated regional reserve/stress model exists yet | Supply/reserve balances, other users, return flows, ecological minimum flows, regional outcome labels |
| Document context | TF-IDF/FAISS word search, geographic eligibility, exact quotations; fictional test documents | Real municipal permits, environmental impact statements, EPA assessments, relevance/applicability review |
| Reliability | Synthetic model comparisons, missingness tests, clipping tests, range-coverage checks | Independent calibration and tests holding out areas, seasons, and drought periods |

The public-data two-day sample demonstrates downloading and parsing. The model's
water-use labels are synthetic. Neither validates regional environmental impact.
The existing `/forecast` contract requires facility inputs and returns on-site cooling
consumption under `predicted_collateral_stress_mgd`. Keep that contract documented
accurately until a separate area assessment is implemented.

## How an area assessment should work

1. Identify the area and seasonal baseline, with verified watershed and utility boundaries.
2. Collect dated conditions and quality flags. Keep flow in MGD, groundwater depth in
   meters, and PDSI dimensionless. Groundwater level is not a recharge rate.
3. Describe the proposed development's demand alongside existing demands and water
   returned to the area. Use the cooling model only for the pressure it actually estimates.
4. Compare the added pressure with regional supply, reserves, and verified environmental
   thresholds. Define and validate each regional target before training a stress model.
5. Report interpretable seasonal indicators, their uncertainty and missing-data limits,
   and source-matched document excerpts. Do not invent a combined ecosystem score.

These steps describe the intended regional system, not completed features. An area-wide
assessment needs observed outcomes and tested relationships, not a renamed cooling estimate.

## Use the supplied context without inventing experiment results

- Symbolic heat rules are implemented and tested as component safety rails. A historical
  heatwave/humidity validation study is planned; the rules are not regional ecological limits.
- RF/XGBoost comparisons are completed on synthetic cooling-water targets. The stated
  R2 > 0.80 / MAE < 0.05 MGD goal belongs to that target; it does not validate regional stress.
- A zero-shot LLM comparison was not run. Rejecting unconstrained LLM numerical or legal
  judgments is a design choice based on anticipated risks, not an observed benchmark result.
- Current retrieval uses sparse TF-IDF word vectors, not dense learned embeddings. Dense
  embeddings/generative summaries remain proposals. Numeric calculations stay separate.
- Missingness tests use synthetic streamflow and a separate groundwater-depth reconstruction.
  Historical 2015-2022 recharge masking, multi-month drought validation, and conversion from
  groundwater conditions to regional stress remain planned.
- Prediction intervals and missingness sensitivity bands answer different questions. The
  observed cooling-model coverage is about 88% against a 90% goal; R2 is not confidence.
- EIA/EPA usage profiles and regional assessments are proposed sources, not a completed
  ingestion or validated document collection. Check each actual product's access and rights.

## Next question and team ownership

**Next question:** Can verified area conditions and development-demand evidence support
an accurate seasonal assessment of municipal reserves and watershed stress in an area
not used to build the model?

Shaun leads coding, architecture, area-assessment integration, and separate calibration.
Troy supports environmental data acquisition, station/area validation, drought/recharge
interpretation, and document grounding. Scott supports safety-rule evaluation, interface
review, failure analysis, regional evidence selection, diagrams, slides, and rehearsal.
Shaun's coding lead is confirmed; supporting duties are assigned, not certified complete.

The regional purpose follows the user's October 8 context and correction. Historical
implementation notes and raw experimental evidence remain intact. Course materials must
describe the regional goal and present the existing component tests within their actual scope.
