# ECOllateral in plain English

## The 20-second explanation

ECOllateral asks how new development could affect an area's water supply and rivers
through the year. Our demo estimates cooling water use, checks the number, and adds
quotes from local permits. Cooling is one example. We still need real measurements
of water coming in, water used and returned, and water needed by rivers.

## The goal and the part we can demonstrate

Town planners, researchers, and water providers need to know how development changes
the surrounding ecosystem. A watershed is land that drains into the same river system.
Start with the area's water and weather, then look at water use. Cooling is one example.
The full area assessment is still to build and test. `../project-scope.md` lists what
works now and what we still need.

## One easy takeaway per slide

| Slide | What to say |
| --- | --- |
| 1. Problem & users | We want to explain how development affects water across an area |
| 2. Semantic map | AI estimates water use, rules check it, and local permit quotes add context |
| 3. Experiment E1 | XGBoost made smaller errors on our made-up test data |
| 4. Experiment E2 | Gap filling worked on similar stations, but high neighbor readings caused problems |
| 5. Experiment E5 | Our ranges included about 88% of test values, below the 90% goal |
| 6. Decisions & next question | Keep the tested parts, improve the weak points, and test real area data |

Keep **Semantic Map**, **Experiment**, **Evidence**, **Failure / Reliability Issue**,
and **Adopt / Modify / Reject / Defer** visible because these identify the A2 sections.
Explain them in ordinary words: how it works, what we tested, what happened, what went
wrong, and what we keep, change, do not use, or wait to try.

## Explain the current component in five steps

1. **Collect data.** USGS provides river measurements; NOAA provides weather and drought
   data. Each value keeps its unit, station name, date, and quality information.
2. **Build six inputs.** Facility size, two temperature readings, river flow, drought
   score, and season. The model learns from these inputs and a water-use target.
3. **Estimate water use.** Compare two tree-based AI methods: RandomForest and XGBoost.
   Use a separate model for each cooling type.
4. **Check the number.** Calculate physical limits using facility load and heat removal.
   Move an out-of-range estimate to the nearest limit and show a warning.
5. **Add context.** Search permit sections by words, then check their location. Return
   the original quotations and sources alongside the estimate.

The two paths in the map are the **number path** and the **permit path**. They meet in
the API response. The API is the interface that lets another program request a result.
These component tests support the regional project, but the API's current cooling
number is not an ecosystem health score or a municipal reserve forecast.

## The experiments, in one sentence each

| ID | Easy explanation | Result and decision |
| --- | --- | --- |
| E1 | Which AI method makes smaller errors? | XGBoost has lower error for both evaporative types on made-up labels; keep it and retain RandomForest for comparison |
| E2 | What happens when drought measurements are missing? | Both filling methods pass on similar made-up stations; a separate biased-neighbor test exposes a weakness, so improve the tests |
| E3 | What if the AI returns an impossible number? | Deliberately wrong predictions are moved into the physical range and flagged; keep this safeguard |
| E4 | Does a permit match the requested place? | Four made-up document tests pass the location rules; keep them and test real permits next |
| E5 | Do the prediction ranges include enough test values? | About 88% are inside ranges intended for 90%; improve how the ranges are set and evaluated |

The main drought experiment uses the fitted model. The biased-neighbor diagnostic
uses a different, simple formula. Do not describe its 60.33% result as the fitted
model's failure rate.

## Terms you can translate while presenting

| Technical term | Plain-English meaning |
| --- | --- |
| Synthetic data | Made-up data generated for testing; not measurements from real facilities |
| Feature | One input the AI uses |
| Label / target | The water-use value the AI is trained to predict |
| Regression / regressor | Predicting a number / the model that predicts it |
| RandomForest (RF) | A model that combines many decision trees |
| XGBoost (XGB) | A model that adds trees to improve earlier prediction errors |
| Baseline | A method kept as a point of comparison |
| MW | Megawatts; here, the IT equipment's installed power capacity |
| MGD | Million US gallons per day; the water-use and river-flow unit |
| Dry bulb / wet bulb | Ordinary air temperature / a temperature related to evaporative cooling; both in C |
| PDSI | Palmer Drought Severity Index; the experiment calls values <= -2 drought |
| HUC8 | An eight-digit code identifying a watershed; keep leading zeros |
| PUE | Power Usage Effectiveness: total facility power divided by IT power; default 1.2 |
| WUE | Water Usage Effectiveness: site water in liters per kWh of IT energy |
| Utilization | The assumed fraction of available IT load in use; default 1.0 |
| Bounds / clipping | Calculated limits / moving an estimate to the nearest limit |
| MAE | Mean absolute error: the average size of a prediction error; lower is better |
| RMSE | Root mean square error: a score that gives larger errors more weight; lower is better |
| R2 (R-squared) | A measure of model fit; it is not the probability the prediction is right |
| Calibration | Setting a model's prediction range using separate example errors |
| Held-out test | Data saved for evaluation rather than model training or selection |
| Coverage | The fraction of test values inside the prediction range |
| Interval width | How wide the prediction range is |
| Missingness / imputation | Missing measurements / filling the gaps |
| Spatial donor | A nearby station used to fill a missing reading |
| Linear interpolation | Filling a gap along a straight line between earlier and later readings |
| Variance / standard deviation | Two measures of how much predictions change; units here are MGD2 / MGD |
| Sensitivity band | A range showing changes caused by missing data; not a future forecast interval |
| TF-IDF | Term frequency-inverse document frequency: scores words by how informative they are |
| Vector / FAISS | A numeric representation of text / the library used to search those representations |
| Metadata | Information attached to a document, such as source, section, and location |
| Retrieval / top-k | Finding relevant sections / keeping up to k eligible results |
| Extractive summary | Text built from existing quotations rather than newly invented permit language |
| Geographic scope | The place a document is marked as covering; it still needs human review |
| Provenance / SHA-256 | Where data came from / a fingerprint used to detect file changes |

## Numbers worth remembering

- **Model data:** 1,600 made-up rows per cooling type across six years; random seed 42.
- **Split:** oldest 60% of dates train the model, next 20% select it and set its range,
  newest 20% test it. Reusing the middle group for two jobs is a limitation.
- **Model result:** tower average error improves from 0.004890 to 0.003668 MGD;
  direct evaporation improves from 0.003842 to 0.003191. Each test group has 333 rows.
- **Range result:** tower coverage 88.29% (294/333); direct 87.99% (293/333); target 90%.
- **Drought test:** 365 dates, 121 drought dates, 10/25/40% gaps, 50 repeats, +/-0.05 MGD
  tolerance. All six main comparisons pass on the made-up stations.
- **Biased-neighbor diagnostic:** add 100 MGD to neighbors; 40% gaps; 20 repeats;
  `prediction = 0.01 * streamflow`; spatial coverage 60.33%, linear 98.60%.
- **Rule test:** 40 MW, 30 C dry bulb, 20 C wet bulb gives 0 to 0.446484 MGD.
  Forced -1 and 1,000,000 MGD predictions are clipped and flagged.
- **API example:** the 40 MW tower scenario returns about 0.204339 MGD with source warnings.
- **Software checks:** 51 tests passed, with one upstream deprecation warning.

## Keep these limits in the explanation

The current number is on-site cooling consumption. It does not measure area-wide
ecosystem impact, municipal reserves, or total water stress. Historical monthly weather is a scenario input, not a future weather
forecast. Nearby stations may behave differently. Linear gap filling can use later
readings, which a live forecast would not yet have. A matching permit quotation is
context for a person to review, not a legal compliance decision.

The physical limits use assumptions; they are not universal engineering guarantees.
The 88% range coverage is from finite, made-up samples, and no significance test was
run. Neural models and generative LLMs were not compared. The full dossier retains
the methods, exact evidence references, decisions, and course requirements.

## Who explains what

Shaun: what the system does and the model comparison (slides 1-3).
Troy: missing data and prediction ranges (slides 4-5).
Scott: decisions and the next test (slide 6).

Shaun's coding lead is confirmed. Troy's and Scott's supporting roles are assigned;
each member still needs to confirm their actual completed work before submission.
