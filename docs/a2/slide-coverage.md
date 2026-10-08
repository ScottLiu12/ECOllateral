# A2 slide coverage audit

Checked against all three pages of the user-supplied
`CSCI4150_A2_MidSemester_System_Evidence_Review.pdf`. The course brief defines the
review requirements; it does not authorize submission or access changes. This audit
maps the current six-slide deck and notes to those requirements without predicting a grade.

## Labels visible on the slides

| Slide | Exact section heading | Additional requirement label |
| --- | --- | --- |
| 1 | Problem & users: ecosystems across an area | Project goal / Working demo; intended users named |
| 2 | Semantic map: current system | Six inputs, learned cooling use, physical rules, words as numbers, source/location details; E3/E4 evidence |
| 3 | Experiment E1: comparing AI models | Comparison chart, selection method, evidence source |
| 4 | Experiment E2: missing readings | FAILURE: high readings (neighbor stations) |
| 5 | Experiment E5: prediction ranges | RELIABILITY ISSUE: below the 90% goal |
| 6 | Decisions & next question | KEEP (ADOPT), CHANGE (MODIFY), DO NOT USE (REJECT), WAIT (DEFER); area next question |

Experiment IDs match the dossier and evidence table. E3/E4 remain additional safeguard
investigations on the semantic map; E1, E2, and E5 each have a dedicated chart slide.
Slides 2-5 explicitly label their source footers **Evidence:** with matching result files.
The visible text uses ordinary words. The spoken script comes first in the notes, with
full methods and technical terms under **Extra details for questions**. For example,
"words as numbers" explains vectors and "source/location details" explains metadata.
Model names and the experiment IDs remain so the audience can follow the evidence.

## Seven required things to show

| A2 requirement | Where the audience sees it | Evidence or supporting material |
| --- | --- | --- |
| 1. Problem and intended user/setting | Slide 1 asks about development effects on seasonal area reserves/watersheds; names municipal planners, researchers, utilities | Regional goal versus current prototype; `../project-scope.md`, dossier section 1 |
| 2. Current semantic/system map | Slide 2 shows observations/units, six features, cooling-use target, tree models, heat rules, document words, vectors, source/location metadata, eligible quotations | Editable number/document paths; standalone map; notes explain what is implemented versus planned |
| 3. At least three meaningful investigations | E1 model comparison on slide 3; E2 gap filling on slide 4; E5 range evaluation on slide 5; E3/E4 safeguards on slide 2 | Four approach investigations plus range investigation, not an invented LLM experiment |
| 4. Concrete inspectable evidence | Three editable charts on slides 3-5; E3 clipping range and four E4 location tests on slide 2 | Referenced CSV/JSON in `evidence/`; chart workbooks; notes retain setup, sample counts, units, and source paths |
| 5. Consequential failure/limitation | Biased-neighbor diagnostic on slide 4; 88.3%/88.0% versus 90% goal on slide 5; no validated regional assessment on slide 1 | Explain separate diagnostic formula, synthetic labels, reused calibration split, and limits of interpreting finite samples |
| 6. Evidence-supported decisions | Slide 6 separates Adopt, Modify, Reject, Defer and connects each to E1-E5 or an explicit absence of evidence | Lower XGBoost error; safeguards pass; biased donors/coverage need changes; R2 is not confidence; regional data/LLM benchmarks missing |
| 7. Most important next question | Slide 6 asks about seasonal reserve/watershed impacts in an unseen area | Regional supply/demand/returns, ecological baselines, target definitions, independent calibration, and area holdouts |

## Rubric and timing

- **20 points, problem/map:** area-first purpose, intended users, current component diagram,
  meaningful features/target/rules/vectors/metadata, and current-versus-planned distinction.
- **25 points, experiments/evidence:** comparable model results, repeated missingness study,
  coverage counts, fault-injection behavior, and geographic retrieval outcomes with sources.
- **15 points, failure interpretation:** what biased donors and interval shortfall reveal,
  why generated targets do not validate regional impact, and what must change next.
- **20 points, design/rationale:** explicit decisions with evidence IDs and reasons on slide 6.
- **10 points, AI connections:** slide 2 explains how numerical tree models, symbolic rules,
  word-vector search, metadata filtering, and quotations complement one another. No dense
  embeddings, neural model, or generative LLM comparison is represented as completed.
- **10 points, presentation/questions:** six readable slides, 240-second script, evidence-specific
  Q&A, three proposed speaking roles, full technical notes and portable supporting evidence.

Timing follows the handout's suggested structure: slides 1-2 are 60 seconds for the
problem/map; slides 3-5 are 120 seconds for experiments/failures; slide 6 is 60 seconds
for decisions/next question. Allow another two minutes for questions/transition.

## Five required submission components

| Component | Prepared files |
| --- | --- |
| A. Curated dossier snapshot | `dossier.md`, `dossier.pdf`, selected `evidence/` files |
| B. One readable current semantic/system map | `semantic-system-map.svg`, `.png`, dossier diagram, editable slide 2 |
| C. Approach/evidence/decision summary | `evidence-summary.csv`, dossier decision table, slide 6 |
| D. Concise presentation materials | `review-slides-simplified.pptx`, `review-slides.pdf`, `presentation-script.md` and Q&A |
| E. One line per teammate | `team-contributions.md`; supporting duties remain assigned, not certified finished |

The slides are the concise review, not the entire dossier. A2 explicitly does not require
a finished system, every class technique, successful results from every experiment, or
large amounts of new presentation-only work. Keep the failed/limited results visible.

## Human checks still required

Rehearse with all three members, confirm that everyone can explain the architecture
and evidence, verify actual contributions, confirm October 20/23 assignment and the
posted Submitty deadline, and complete instructor-access/office-hours checks. Course
studio names/links still need confirmation. Local files cannot establish those actions.
