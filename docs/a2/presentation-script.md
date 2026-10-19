# Four-minute talk

Six slides, followed by two minutes for questions. Speaking roles: Shaun, slides 1-3;
Troy, slides 4-5; Scott, slide 6.

## Slide 1: local water and new development

ECOllateral asks how a new building could affect local water supplies and rivers.
It is for town planners, researchers, and water providers. We started with one
part of the problem: water used to cool equipment. The current program estimates
that daily use and shows local permit quotes. Our examples use generated water-use
data. We need actual measurements before we can judge how well it works at real sites.

## Slide 2: how the program works

Six numeric features represent equipment size, air and wet-bulb temperature, river
flow, drought, and season. XGBoost's learned trees estimate daily water use. Symbolic
energy rules constrain the estimate. A separate permit path uses TF-IDF word vectors
and location metadata to find local passages. The result combines gallons per day,
a prediction range, warnings, and exact quotes. A person decides permit applicability.

## Slide 3: which model makes smaller errors?

We compared two models called RandomForest and XGBoost. Both learn from examples.
The chart shows the average size of their mistakes, in gallons per day. Lower is
better. For cooling towers, XGBoost reduced the average error from about 4,900 to
3,700 gallons per day. It also did better for direct evaporation. Each method had
333 test examples. We kept XGBoost, but this result is still against generated answers.

## Slide 4: what if river readings are missing?

We tried two ways to fill a missing reading: use a nearby station, or use the
readings before and after the gap. With similar stations, both worked well in our
generated examples. Then we made the nearby readings too high. In that separate
test, the nearby-station method stayed close only 60 percent of the time. Filling
between dates reached about 99 percent. That test used a simple formula. The lesson
is that a nearby reading is useful only if it represents the same conditions.
Filling between dates requires later readings, so it suits historical gaps.

## Slide 5: did the prediction range work?

The program gives a low and high estimate. We wanted that range to contain 90 out
of every 100 test answers. It contained about 88 for both cooling methods. That
missed our goal. We also used the same data to choose the model and set its range.
We should separate those jobs and test again with measured water use. A good model
fit alone does not tell us whether its range is useful.

## Slide 6: what we will keep and improve

E1 supports keeping XGBoost; E3 supports physical checks; E4 supports local quotes
with real-permit testing still needed. E2 changes our donor checks; E5 calls for
separate calibration data. E1 and E5 show why we reject fit as a promise of accuracy.
We defer neural and language models until we can compare them fairly. The next
step is to train on some sites and test on different sites. To answer the bigger
local-water question, we also need other water uses, water returned, available
supply, and the water rivers need.

## Short answers for questions

- **What is a model?** A program that learns patterns from examples and uses them
  to estimate an answer for a new input.
- **What did the two models learn?** The link between equipment size, weather,
  river conditions, season, and daily cooling water use in generated examples.
- **What does training and testing mean?** Training teaches the model. Testing uses
  examples held aside to measure its mistakes.
- **What is a watershed?** Land that drains into the same river system.
- **Why use generated data?** It lets us check the program before we have measured
  facility water use. The public weather and river readings do not supply that answer.
- **What did the bad-reading test measure?** How much the output changed after
  filling gaps. It used a separate simple formula, not the fitted model.
- **Why not always fill between dates?** It needs a later reading, which is not
  available during a live gap.
- **What are the physical and location checks?** Impossible numbers are adjusted
  and flagged. Permit passages must match the requested place. All four fictional
  location cases passed. Neither check proves an estimate is accurate.
- **What are the AI methods called?** RandomForest and XGBoost are tree models:
  a tree asks a series of simple questions. RandomForest averages many trees.
  XGBoost adds trees to correct earlier mistakes. Permit search compares word scores (TF-IDF)
  and then checks location. It does not use a language model to write new permit text.
- **Where are the exact methods and numbers?** The [dossier](source/dossier.md),
  [evidence files](evidence/README.md), and [implementation notes](../implementation-notes.md).
