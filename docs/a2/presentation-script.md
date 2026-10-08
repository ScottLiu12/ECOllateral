# Four-minute talk and Q&A

Allow 4 minutes for the talk and
2 minutes for questions.

## Slide 1: problem & users — ecosystems across an area

ECOllateral asks how new development could affect an area's water supply and rivers
through the year. It is for town planners, researchers, and water providers. Our working
demo estimates cooling water use, checks physical limits, and adds local permit quotes.
Cooling is one example. Current tests use computer-generated water-use examples to
check the software. Next, collect real measurements, train on them, and test on records
the model has not seen. We still need area water totals and river needs.

## Slide 2: semantic map — current system

The semantic map shows what each part means and how it connects. Six inputs describe
size, two temperatures, river flow, drought, and season. AI predicts cooling water use.
Rules check power and heat limits. The text path turns words into numbers to find local
permit quotes with sources. All four location tests pass. Forced wrong numbers move
inside the limits and trigger warnings. A person reviews the permit rules.

## Slide 3: experiment E1 — comparing AI models

We tested two AI models on the same made-up water-use values. RF means RandomForest.
Lower bars mean smaller
errors. XGBoost made smaller errors for both cooling types. Tower error fell from about
0.00489 to 0.00367 million gallons per day. Direct cooling error fell from 0.00384 to
0.00319. Each test group has 333 rows. We use the oldest 60 percent of dates to teach
the model, the next 20 percent to choose it and set its range, and the last 20 percent
to test it. We keep RandomForest to compare. Dry air cooling uses zero water here.
Next, train on real water-use measurements and test on separate real records.

## Slide 4: experiment E2 — missing readings

We removed 10, 25, and 40 percent of drought readings and repeated each test 50 times.
We filled gaps using a nearby station or a straight line between readings. Lower bars
mean predictions changed less. All main tests stayed within 0.05 million gallons per
day of the result with no missing data. Our made-up stations act alike. What if a
neighbor reads too high? In a separate test, we added 100 million gallons per day to
neighbor readings. Only 60.3 percent stayed within limits. That test uses a simple
formula. Next, test bad readings, long gaps, and stations losing data together.

## Slide 5: experiment E5 — prediction ranges

A prediction range gives a low and high estimate. Our goal was to include 90 percent
of test values. We reached 88.3 percent for towers and 88.0 percent for direct cooling.
That is below our goal. We have not checked whether the difference is more than chance.
The fit score, called R-squared, is high, but it cannot promise a useful range.
We used the same data to choose the model and set its range. Next, use separate data
for those jobs and test other facilities, dates, and drought conditions.

## Slide 6: decisions & next question

Keep, change, do not use, and wait are our four decisions. We keep XGBoost because its
errors are smaller, along with the tested limits and location checks. We will improve
gap filling and prediction ranges because the bad-reading test and the 90 percent goal
show weaknesses. Next, collect real measurements, train on them, and test new areas.
We must add water coming in, water used and returned, and river needs.
A cooling-water estimate alone cannot show ecosystem health. A fit score cannot promise
a correct answer. We also cannot let a language model invent a risk score. We will wait
for real area measurements before comparing more AI methods. We have not run those
comparisons yet. Shaun leads coding. Troy supports data and source quotes. Scott supports
tests and results. Those supporting duties still need confirmation. Our next question:
can training on real data predict effects on water reserves and rivers in a new area
through the year?

## Short answers for Q&A

- **What is a watershed?** Land that drains into the same river system. Its weather
  and water use affect the river and nearby water supplies.
- **What does "semantic map" mean?** A diagram showing what the information means
  and how the parts use it. Features are inputs. The target is the value we want
  to predict. Word vectors turn text into numbers. Metadata means source and location details.

- **Is this a data-center project?** We study how development affects an area's
  ecosystem. Cooling water is one example in the current demo.
- **Do you already predict ecosystem health or town reserves?** No. We need area
  water totals, river needs, and real tests before we can make those claims.
- **Did you test language models or groundwater recharge?** No. Those are planned
  studies. Our tests use made-up cooling and river-flow values. Groundwater depth
  is a separate measurement, in meters. It does not tell us how fast water is replaced.

- **Is the accuracy result real-world evidence?** No. Water-use targets are made up.
  The two-day public-data download tests parsing and units, not forecast accuracy.
- **Should we train on real data?** Yes. Generated examples check the first prototype.
  The finished model needs measured inputs and outcomes. We will train on historical
  records and test on different records and areas. Public weather or river readings
  alone cannot tell us the correct water-use or area-impact answer for training.
- **Why XGBoost?** It had smaller errors when we chose the models and when we tested
  them. The selection score is RMSE, which gives large errors more weight. Keep
  RandomForest to compare against future results.
- **What does 90% mean?** The intended fraction of values inside the prediction range.
  We measured about 88%. Missing-data tests measure how much results change when
  readings disappear. That is a different question.
- **Is 88% meaningfully worse than 90%?** We did not check whether the difference
  is more than chance. We missed the goal in this test. Next, set ranges using
  separate data and show how much the measured percentage could vary.
- **What AI did you actually test?** RandomForest and XGBoost predict numbers.
  We also tested gap filling, physical rules, and permit word search. TF-IDF turns
  words into numbers. FAISS searches them. Source and location details help select
  the right quotes. We did not compare neural models or language models that write
  new answers. Exact class studio names still need checking.
- **Do physical limits guarantee the right answer?** No. They enforce our assumptions
  about power, heat, and which water uses count. PUE means total facility power
  divided by equipment power. Those assumptions need engineering review.
- **Does a permit match prove compliance?** No. It gives a source quotation for a
  person to review. We still need to check real permits and whether their rules
  apply to the request.
- **Can a watershed code stand in for facility coordinates?** No. A watershed match
  and a match within a distance are different. A river station's location cannot
  tell us the facility's exact location. The watershed code is called HUC8.
- **Why keep groundwater in meters?** It is a depth. Turning it into MGD needs geometry
  and a model of how water moves. Depth and flow measure different things.
- **Can you fill a live gap with a straight line?** Our historical method can use a
  later reading. A live forecast needs a method using only readings available then.

## Before presenting

- Rehearse to 240 seconds. Explain the result rather than reading every table row.
- Keep the system map and evidence files ready for questions.
- Make sure all three members can explain made-up data and decisions E1-E5.
- Confirm presentation day, deadline, instructor access, and office hours externally.
- Confirm each member's actual contribution before submitting the one-line statements.

## Details to keep ready, rather than say during the timed talk

Use the guide and glossary below for definitions and memorable numbers. The dossier retains
all exact metrics, setups, sources, and limits. In particular: R2 is undefined for
the constant-zero dry-air target; the middle date group is reused for selection and
range sizing; the biased-neighbor diagnostic is not the trained model; linear filling
can use future readings; and a permit quotation is not a compliance decision.

## Project guide and glossary

### The 20-second explanation

ECOllateral asks how new development could affect an area's water supply and rivers
through the year. Our demo estimates cooling water use, checks the number, and adds
quotes from local permits. Cooling is one example. We still need real measurements
for training and separate testing, plus water coming in, water used and returned, and
water needed by rivers.

### The goal and the part we can demonstrate

Town planners, researchers, and water providers need to know how development changes
the surrounding ecosystem. A watershed is land that drains into the same river system.
Start with the area's water and weather, then look at water use. Cooling is one example.
The full area assessment is still to build and test. `../project-scope.md` lists what
works now and what we still need.

### One easy takeaway per slide

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

### Explain the current component in five steps

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

### The experiments, in one sentence each

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

### Terms you can translate while presenting

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

### Numbers worth remembering

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

### Keep these limits in the explanation

The current number is on-site cooling consumption. It does not measure area-wide
ecosystem impact, municipal reserves, or total water stress. Historical monthly weather is a scenario input, not a future weather
forecast. Nearby stations may behave differently. Linear gap filling can use later
readings, which a live forecast would not yet have. A matching permit quotation is
context for a person to review, not a legal compliance decision.

The physical limits use assumptions; they are not universal engineering guarantees.
The 88% range coverage is from finite, made-up samples, and no significance test was
run. Neural models and generative LLMs were not compared. The full dossier retains
the methods, exact evidence references, decisions, and course requirements.

### Who explains what

Shaun: what the system does and the model comparison (slides 1-3).
Troy: missing data and prediction ranges (slides 4-5).
Scott: decisions and the next test (slide 6).

Shaun's coding lead is confirmed. Troy's and Scott's supporting roles are assigned;
each member still needs to confirm their actual completed work before submission.
