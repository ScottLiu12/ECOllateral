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

There are four steps. First, enter the equipment size, cooling method, place, and
month. The program adds weather and river readings. Second, a model learns from
examples and estimates water use. Third, a separate calculation checks that the
number fits the cooling assumptions, and a word search finds local permit passages.
Finally, the program returns daily water use, a range, warnings, and the quotes.
It does not decide whether a project meets its permit.

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

## Slide 5: did the prediction range work?

The program gives a low and high estimate. We wanted that range to contain 90 out
of every 100 test answers. It contained about 88 for both cooling methods. That
missed our goal. We also used the same data to choose the model and set its range.
We should separate those jobs and test again with measured water use. A good model
fit alone does not tell us whether its range is useful.

## Slide 6: what we will keep and improve

We will keep the model comparison, physical checks, and local permit quotes.
We will improve how missing readings and prediction ranges are handled. We will
wait on more complicated AI while we collect measured water-use examples. The next
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
