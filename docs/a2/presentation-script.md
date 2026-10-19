# Four-minute presentation script

Read the six slide sections aloud. The Q&A below is a reference, not part of the talk.
Allow two more minutes for questions and transition.

**Speakers:** Shaun: slides 1-3. Troy: slides 4-5. Scott: slide 6.

## Slide 1: local water and new development - 25 seconds

ECOllateral asks: how could a new building affect local water supplies and rivers?
Our intended users are town planners, researchers, and water providers.

Our prototype estimates one part of that problem: daily water use for cooling
equipment. It does not yet measure the full environmental impact. Our test data
is generated, so we still need measurements from real facilities.

## Slide 2: how the program works - 40 seconds

The user enters equipment size, cooling method, location, and month. We add saved
weather and river readings to form six numeric inputs: equipment size, air
temperature, wet-bulb temperature, river flow, drought, and month. Wet-bulb
temperature accounts for humidity, which affects evaporative cooling.

XGBoost learns patterns from examples to estimate daily water use. Physical energy
rules check whether that estimate fits our cooling assumptions.

A separate search uses TF-IDF, which scores matching words, plus location filters
to find local permit passages. The output includes gallons per day, a prediction
range, warnings, and exact quotes. A person must judge how the permit applies.

## Slide 3: which model makes smaller errors? - 30 seconds

We compared RandomForest and XGBoost. Both learn through decision trees: sequences
of simple questions about the inputs.

We tested them on examples held out of training. The chart shows average error in
gallons per day; lower is better. For cooling towers, XGBoost reduced error from
about 4,900 to 3,700 gallons per day. It also performed better for direct evaporation.

That supports choosing XGBoost for this prototype. It does not prove real-world accuracy.

## Slide 4: what if drought readings are missing? - 40 seconds

We tested two ways to fill missing drought readings: borrow from a nearby station,
or estimate between readings before and after the gap.

Both worked well with similar generated stations. In a separate test, we made the
nearby readings too high. Only 60 percent of output changes stayed within our
50,000-gallon-per-day tolerance, compared with 99 percent for filling between dates.
This diagnostic used a simple formula, not our trained model.

The lesson: nearby stations must represent similar conditions. Filling between
dates needs a later reading, so it suits historical gaps.

## Slide 5: did the prediction range work? - 30 seconds

A prediction range expresses uncertainty around the estimate. Our goal was to
include 90 out of every 100 test answers. We reached about 88 for both water-based
cooling methods, so we missed the target.

We also reused the same data to choose the model and set the range. Next, we will
separate those tasks and test again. Small average errors do not guarantee a
reliable prediction range.

## Slide 6: what we will keep and improve - 45 seconds

Our evidence guides four decisions.

We **keep** XGBoost because of its lower errors in E1, physical checks from E3,
and location-filtered permit quotes from E4. The permit tests used fictional documents.

We **improve** station checks after E2 and use separate data to set prediction
ranges after E5. We **reject** treating a good model fit as guaranteed accuracy.
We **defer** neural networks and language models until we can compare them fairly.

Our next question is whether a model trained on some real facilities works at
different facilities. Answering the broader water-impact question also requires
available supply, other water uses, returned water, and river needs.

## Short answers for questions

- **What is training versus testing?** Training teaches patterns; testing checks
  predictions against answers the model did not learn from.
- **What do the models do differently?** RandomForest averages many trees.
  XGBoost adds trees that correct earlier errors.
- **What does MGD mean?** Million US gallons per day. The example forecast is about
  0.204 MGD, or 204,000 gallons per day.
- **Why generated data?** It lets us test the pipeline before we obtain measured
  facility consumption. Weather and river data do not provide that target.
- **What are the physical checks?** Estimates outside calculated cooling limits
  are adjusted and flagged; the original value remains visible.
- **What did the permit tests show?** All four fictional location cases behaved
  as expected. That checks filtering, not real-permit relevance or compliance.
- **What is calibration?** Using held-out examples to set the prediction range.
  Those examples should be separate from model selection and final testing.
- **What is a watershed?** An area of land draining into the same river system.
- **Where is the evidence?** The [dossier](source/dossier.md),
  [saved results](evidence/README.md), and [methods](../implementation-notes.md).
