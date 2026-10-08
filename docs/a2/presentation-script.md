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

## Slide 1: problem & users — ecosystems across an area

ECOllateral asks how new development could affect an area's water supply and rivers
through the year. It is for town planners, researchers, and water providers. Our working
demo estimates cooling water use, checks physical limits, and adds local permit quotes.
Cooling is one example. We still need area water totals and river needs. The AI learns
made-up water-use values, so real area tests are still needed.

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
Next, we need real water-use and area measurements.

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
show weaknesses. We must add water coming in, water used and returned, and river needs.
A cooling-water estimate alone cannot show ecosystem health. A fit score cannot promise
a correct answer. We also cannot let a language model invent a risk score. We will wait
for real area measurements before comparing more AI methods. We have not run those
comparisons yet. Shaun leads coding. Troy supports data and source quotes. Scott supports
tests and results. Those supporting duties still need confirmation. Our next question:
can we test effects on water reserves and rivers in a new area through the year?

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

Use `explain-it-simply.md` for definitions and memorable numbers. The dossier retains
all exact metrics, setups, sources, and limits. In particular: R2 is undefined for
the constant-zero dry-air target; the middle date group is reused for selection and
range sizing; the biased-neighbor diagnostic is not the trained model; linear filling
can use future readings; and a permit quotation is not a compliance decision.
