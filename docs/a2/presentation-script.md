# Four-minute talk and Q&A

Assigned day: still unknown, October 20/23, 2026. Allow 4 minutes for the talk and
2 minutes for questions. These speaking roles are proposed; rehearse together.

| Slide | Speaker | Seconds | End time | Main point |
| --- | --- | --- | --- | --- |
| 1 | Shaun | 30 | 0:30 | The problem and what works |
| 2 | Shaun | 30 | 1:00 | How the system works |
| 3 | Shaun | 45 | 1:45 | Which model made smaller errors |
| 4 | Troy | 40 | 2:25 | Missing data and bad neighbors |
| 5 | Troy | 35 | 3:00 | Prediction ranges missed the goal |
| 6 | Scott | 60 | 4:00 | Decisions, roles, and next test |

## Slide 1: ecosystem impacts across an area

ECOllateral aims to help planners, researchers, and utilities understand how proposed
development affects an area's municipal water reserves and watershed conditions across
seasons. The ecosystem and area are the focus. Our prototype connects environmental
data, a cooling-water pressure model, physical checks, and local permit quotations.
Cooling is one component test. The regional supply, demand, return-flow, and ecological
assessment is still planned. Our model targets are made-up data, so we are not claiming
validated regional impact forecasts yet.

## Slide 2: two paths, one response

This diagram shows current components, not the full regional assessment.
The top path handles numbers. Weather, river flow, drought, season, and facility size
become six inputs. A tree-based AI model predicts water use. Separate engineering
rules check the number and warn if it needs adjusting. The bottom path handles permit
text. We search words, check the location, and return original quotations. Tests showed
the limits and four location cases work. No language model calculates water use
or decides compliance.

## Slide 3: compare models for one pressure component

We compared RandomForest and XGBoost using the same made-up inputs and water-use targets.
We split dates in time order: 60 percent to train, 20 percent to choose the model and
set its range, and 20 percent to test. XGBoost lowered average error for towers from
about 0.00489 to 0.00367 million gallons per day. For direct evaporation, it improved
from 0.00384 to 0.00319. Each test group has 333 rows. We kept XGBoost and retained
RandomForest for comparison. Dry air cooling has zero on-site water use in our scope.
These scores show we learned the generated pattern; real water-use measurements are
still the main gap.

## Slide 4: test missing drought readings

We removed 10, 25, and 40 percent of drought readings and repeated each test 50 times.
Filling gaps from a nearby station or a straight line through time kept forecasts within
0.05 million gallons per day of the complete-data result. But our made-up stations
behave similarly. In a separate test, we raised neighboring flow by 100 million gallons
per day. Nearby-station filling then passed only 60.3 percent of the tolerance checks.
That test uses a simple formula, not the fitted AI model. We need tests with biased
neighbors, long gaps, and several stations losing data together.

## Slide 5: check the prediction ranges

The models fit the made-up data well, but their prediction ranges missed our goal.
Ranges intended to include 90 percent of test values included 88.3 percent for towers
and 88.0 percent for direct evaporation. These are finite test samples, not proof of
a statistically significant failure. We also used the same data to choose the model
and set its range. We will separate those jobs and test by facility, time, and drought.
R-squared measures fit; it is not the chance a prediction is right.

## Slide 6: build and validate the regional assessment

We will keep the tested models, component rules, and location checks. Next, connect
development pressures to observed area supply, reserves, other demands, returns, and
ecological flow needs. We must define regional targets and test unseen areas and seasons
with separate calibration. One cooling-water number cannot represent ecosystem health.
We also reject R-squared as confidence and unconstrained language-model risk scoring.
No zero-shot or generative comparison was run. Shaun leads coding and area integration.
Troy supports environmental baselines, drought analysis, and document grounding.
Scott supports safety and interface evaluation, failure analysis, and regional evidence.
These supporting duties still need completion confirmation. Our next question is whether
verified area conditions and development demands can explain seasonal reserve and
watershed impacts in an area not used to build the model.

## Short answers for Q&A

- **Is this a data-center project?** The goal is regional ecosystem impact assessment
  for proposed development. Cooling water is one pressure component in the current demo.
- **Do you already predict ecosystem health or municipal reserves?** No. Regional
  balance, ecological thresholds, cumulative demands, and outcome validation are still needed.
- **Did you benchmark zero-shot LLMs or groundwater recharge?** No. Those passages in
  the supplied context describe proposed work or anticipated risks. Our recorded tests
  use cooling targets, synthetic streamflow, and separate groundwater depth in meters.

- **Is the accuracy result real-world evidence?** No. Water-use targets are made up.
  The two-day public-data download tests parsing and units, not forecast accuracy.
- **Why XGBoost?** It had lower RMSE when we chose the models and lower average error
  on the test dates. RMSE gives bigger errors extra weight. Keep RF for future comparisons.
- **What does 90% mean?** The intended fraction of values inside the prediction range.
  We measured about 88%. Missing-data sensitivity bands describe a different kind of change.
- **Is 88% significantly worse than 90%?** We did not test statistical significance.
  It misses our observed-result goal. Next, use separate calibration data and report
  uncertainty around the measured coverage.
- **What AI did you actually test?** RF/XGBoost, spatial/time gap filling, symbolic
  engineering rules, and TF-IDF/FAISS word search with location metadata. We did not
  compare neural or generative LLM models. Exact class studio names still need checking.
- **Do physical limits guarantee the right answer?** No. They enforce our assumptions
  about load, PUE, evaporation heat, and included water uses. Those need engineering review.
- **Does a permit match prove compliance?** No. It gives a source quotation for a
  person to review. We still need real-document relevance and applicability checks.
- **Can a watershed code stand in for facility coordinates?** No. A watershed match
  and a coordinate-radius match are different. River gauge coordinates are not facility coordinates.
- **Why keep groundwater in meters?** It is a depth. Turning it into MGD needs geometry
  and a separate physical relationship; meters and flow are not interchangeable.
- **Can you fill a live gap with a straight line?** Our historical method can use a
  later reading. A live forecast needs a method using only readings available then.

## Before presenting

- Rehearse to 240 seconds. Explain the result rather than reading every table row.
- Keep the system map and evidence files ready for questions.
- Make sure all three members can explain made-up data and decisions E1-E5.
- Confirm presentation day, deadline, instructor access, and office hours externally.
- Confirm each member's actual contribution before submitting the one-line statements.

## Details to keep ready, rather than say during the timed talk

Use `explain-it-simply.md` for definitions and memorable numbers. The dossier retains
all exact metrics, setups, sources, and limits. In particular: R2 is undefined for
the constant-zero dry-air target; the middle date group is reused for selection and
range sizing; the biased-neighbor diagnostic is not the trained model; linear filling
can use future readings; and a permit quotation is not a compliance decision.
