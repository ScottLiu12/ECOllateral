# ECOllateral: water use and new development

CSCI 4150 A2 | Shaun, Troy, Scott | Results recorded October 7, 2026

## What the project does

We want to help town planners, researchers, and water providers understand how new
buildings could affect local water supplies and rivers. The current program estimates
one part of that problem: water used to cool equipment.

Enter the equipment size, cooling method, location, and month. The program combines
these with saved weather and river readings. It returns estimated water use per day,
a low-to-high range, and quotes from local water permits.

The example 40-megawatt cooling-tower request returns about **204,000 gallons per day**.
A megawatt measures power. This example uses generated data; measured water use is
still needed to test the program at actual sites.

## How it works

![How the prototype works](../semantic-system-map.png)

Meaning lives in six numeric features: equipment size, air temperature, humidity-based
temperature, river flow, drought, and season. Learned trees map them to daily water use
(MGD). Symbolic energy rules constrain that estimate; they complement rather than
replace learning (E1/E3). TF-IDF word vectors rank permit passages, while location
metadata excludes nonlocal matches (E4). Exact quotes provide context, not permission.
Gap filling changes the features the trees receive (E2); interval coverage tests a
different claim from average prediction error (E5). Neural and LLM comparisons are
deferred until measured targets and a real permit evaluation set support a fair test.

## Three tests and what we learned

### E1: Which model makes smaller errors?

We compared RandomForest and XGBoost. Both learn rules from examples. Each cooling method had 1,600 generated examples. Older dates taught the models.
The two methods below each had 333 examples held aside for testing. Smaller average errors are better. Errors below are in US gallons per day.

| Cooling method | RandomForest | XGBoost |
| --- | --- | --- |
| Cooling tower | 4,890 | 3,668 |
| Direct evaporation | 3,842 | 3,191 |

XGBoost made smaller errors, so we kept it. These are errors against generated answers.
Dry cooling uses no evaporated water in this model, so both methods returned zero.

### E2: What if drought readings are missing?

We removed 10%, 25%, and 40% of drought readings and repeated each test 50 times.
We filled gaps using a nearby station or the readings before and after the gap.
With similar generated stations, all prediction changes stayed within 50,000 gallons
per day of the complete-data result.

A separate test made the nearby readings too high. Only **60%** of changes from the
nearby-station method stayed within that limit, compared with **99%** from filling
between dates. This test used a simple formula, not the trained model. Both methods
also failed a stricter check on the range of changes for every drought date.
Nearby readings need checking. Filling between dates needs later readings, so it is
useful for past gaps rather than live estimates.

### E5: Did the prediction range work?

We wanted the low-to-high range to contain 90 out of every 100 test answers.
It contained about **88 out of 100** for both water-based cooling methods:
294 of 333 tower answers and 293 of 333 direct-evaporation answers.

That missed the goal. We used the same middle group of dates both to choose a model
and to set its range. Those jobs should use separate data. We have not tested whether
the small shortfall could be due to chance.

## Other checks: E3 and E4

E3: at 40 MW, a forced **-1 MGD** became **0 MGD**; a forced **1,000,000 MGD**
became **0.446484 MGD**. Both retained the raw value and `constraint_violation` warning.
These limits depend on cooling assumptions.

E4: watershed `02070010` returned `local-huc`; `99999999` returned no passage.
A coordinate-only permit was excluded without coordinates and included with them.
All four cases passed using fictional permits; quotes do not establish compliance.

## Decisions and next step

| Approach | Evidence | Decision |
| --- | --- | --- |
| RF vs. XGBoost (E1) | Tower MAE: 4,890 vs. 3,668 gal/day | Adopt XGBoost for this prototype |
| Gap filling (E2) | Biased donor: 60%; between dates: 99% within tolerance | Modify donor checks; interpolation for past gaps |
| Symbolic limits (E3) | Both injected violations clipped and flagged | Adopt; retain raw value and warning |
| TF-IDF + location (E4) | Four fictional location cases passed | Adopt with real-permit testing pending |
| Prediction intervals (E5) | About 88% coverage vs. 90% target | Modify; separate selection and calibration |
| Fit as accuracy (E1/E5) | Strong fit coexists with missed coverage | Reject; cooling alone is not regional impact |
| Neural/LLM approaches | No fair measured-data comparison yet | Defer until targets and evaluation set exist |

Next, train and test with measured water use at separate sites. An area assessment
also needs other water uses, water returned, available supply, and river needs.
The main question remains: **how would a new development affect local water?**

## Evidence and methods

E1: `../evidence/regression-comparison.csv`. E2: `../evidence/missingness-summary.csv`
and `../evidence/biased-donor-diagnostic.csv`. E3/E4: `../evidence/constraint-failure-cases.json`
and `../evidence/retrieval-cases.json`. E5: `../evidence/interval-coverage.csv`.
Exact methods and assumptions: `../../implementation-notes.md`. Data sources, units,
and the unchecked climate-division match: `../../data-contracts.md`.
Results use the October 7 implementation; permit search now compares word scores
directly without a separate search library. Team roles and course status: `../README.md`.
