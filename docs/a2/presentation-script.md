# Four-minute presentation and Q&A

Presentation day: pending October 20/23, 2026. Budget: 4 minutes plus 2 minutes Q&A.
These are proposed speaking assignments; rehearse and adjust them together.

| Slide | Speaker | Seconds | Cumulative | Purpose |
| --- | --- | --- | --- | --- |
| 1 | Shaun | 30 | 0:30 | Problem and scope |
| 2 | Shaun | 30 | 1:00 | Semantic/system map and component safeguards |
| 3 | Shaun | 45 | 1:45 | RF/XGBoost experiment |
| 4 | Troy | 40 | 2:25 | Missingness experiment and counterexample |
| 5 | Troy | 35 | 3:00 | Interval coverage failure and decision |
| 6 | Scott | 60 | 4:00 | Decisions, roles, and next question |

## Slide 1: problem and users

We are building ECOllateral to compare on-site cooling water demand for proposed data
center scenarios. A researcher or planner supplies capacity, cooling type, watershed,
and month. The system returns consumption in million gallons per day, physical bounds,
an uncertainty interval, warnings, and relevant permit quotations. We have a working
local prototype. Our facility labels are synthetic, so today's evidence concerns the
architecture and experiments, not validated accuracy at real facilities.

## Slide 2: where meaning lives

The upper path represents environmental conditions as six numeric features. Trees
predict consumption, and independent engineering rules bound the result. The lower
path represents permit text as TF-IDF vectors with geographic metadata, then returns
quotations. Fault injection showed impossible values are clipped and flagged. Four
retrieval cases showed the HUC and coordinate rules work. These are separate,
auditable components; the text generator performs no LLM calculations.

## Slide 3: model comparison

Our first investigation compared RandomForest and XGBoost on the same synthetic
features. We used chronological training, calibration, and test dates, selecting by
calibration RMSE. XGBoost reduced held-out mean absolute error from about 0.00489 to
0.00367 MGD for cooling towers, and from 0.00384 to 0.00319 for direct evaporation.
Each test set has 333 rows. We adopted XGBoost while retaining the forest baseline.
Dry air cooling has a constant zero on-site water label, so its R-squared is undefined.
The strong scores show that we learned the synthetic response surface; measured
facility labels are still the main gap.

## Slide 4: missingness and donor bias

Our second investigation removed 10, 25, and 40 percent of drought observations,
repeating each condition 50 times. Spatial and linear filling both stayed within
0.05 MGD of the complete-data prediction on our correlated synthetic stations.
That success depended on the donors. In a separate diagnostic, shifting neighboring
streamflow upward by 100 MGD reduced spatial tolerance coverage to 60.3 percent.
That diagnostic uses a simple flow-sensitive predictor, not our fitted model.
We will test biased, contiguous, and shared outages before trusting spatial filling.

## Slide 5: high fit does not establish coverage

Our interval investigation exposes another limitation. The cooling tower model has
R-squared 0.998, but its nominal 90 percent interval covers only 88.3 percent of held-out
labels. Direct evaporation covers 88.0 percent. These are finite synthetic samples,
but they miss our observed-coverage gate. The implementation also reuses calibration
data for model selection and interval sizing. We will separate those steps and
evaluate coverage by facility, drought state, and time. R-squared remains a fit metric,
not a confidence probability.

## Slide 6: decisions and next question

The evidence supports keeping the tree baselines, physical constraints, and
geographically scoped retrieval. It supports modifying the missingness and uncertainty
evaluation. We reject describing R-squared as confidence, and we defer neural or
generative language models because we have not compared them and they do not fix the
label gap. Our next question is whether this constrained model generalizes to measured
consumption at an unseen facility during drought with adequate interval coverage.
Shaun leads code and independent calibration. Troy owns environmental geography and
outage evaluation. Scott owns real permit evidence and presentation review. Those
supporting roles are assigned, and we will confirm actual completed contributions
before submission. The dossier includes the experiments, failure cases, provenance,
and the remaining course logistics.

## Two-minute Q&A preparation

- **Where does the accuracy evidence come from?** Synthetic consumption labels.
  Public ingestion is a two-day parser/unit smoke test. Neither establishes field accuracy.
- **Why XGBoost?** Lower calibration RMSE in both evaporative comparisons; held-out
  MAE also improves. We retain RF so future data can reverse the decision.
- **What does 90% mean here?** A nominal residual interval level. Measured test coverage
  is approximately 88%; drought sensitivity bands answer a different question.
- **Is 88% significantly below 90%?** We did not conduct a significance test. It misses
  the observed prototype gate; finite-sample uncertainty and independent calibration
  belong in the next evaluation.
- **What AI approaches were actually investigated?** RF/XGBoost, spatial/time filling,
  symbolic bounds, and lexical-vector retrieval with geographic metadata. No neural
  or LLM comparison was run; confirm specific studio names against class materials.
- **Do bounds guarantee engineering correctness?** They enforce stated assumptions.
  PUE/utilization, latent heat, and water-use scope require engineering validation.
- **Does retrieval establish compliance?** No. It preserves matching source quotations;
  actual applicability and real-corpus relevance require review.
- **Can a HUC stand in for facility coordinates?** No. HUC eligibility and coordinate
  radius eligibility are distinct. Gauge coordinates are not facility coordinates.
- **Why not convert groundwater depth to consumption?** Depth is measured in meters;
  converting it to MGD needs geometry and a separate physical model.
- **Can linear interpolation run live?** The retrospective method can use future
  observations. A causal strategy must be evaluated separately.

## Rehearsal and handoff checklist

- Keep the spoken portion to 240 seconds; do not narrate every CSV entry.
- Open the system map and evidence files before Q&A.
- Verify that all three members can explain the synthetic scope and E1-E5 decisions.
- Confirm presentation date, deadline, instructor access, and office hours externally.
- Review the proposed contribution lines together before submitting them.
