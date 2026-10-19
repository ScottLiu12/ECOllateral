# A2 assignment coverage

Reviewed October 19, 2026 against the supplied two-page project checkoff, two-page
Project Dossier Student Guide, and three-page A2 Mid-Semester System & Evidence Review.

## Required presentation content

| Requirement | Slides and supporting evidence |
| --- | --- |
| Problem, users, and setting | Slide 1: seasonal development impacts for planners, researchers, and utilities; cooling consumption is the current component |
| Current semantic/system map | Slide 2 visibly labels six numeric features, XGBoost learned trees, symbolic energy rules, TF-IDF vectors, and HUC/location metadata; standalone SVG/PNG uses the same representations |
| At least three meaningful investigations | E1 model comparison (3), E2 gap filling (4), E5 range coverage (5); E3/E4 safeguards on slide 2 |
| Inspectable evidence | Editable charts on slides 3-5; dossier gives both E3 clipped outputs and E4's four geographic cases; saved JSON retains exact values and warnings |
| Consequential failure or limitation | Slide 4: high nearby readings yield 60% within tolerance in a separate formula test; slide 5: about 88 in 100 answers inside the range versus a goal of 90; generated data and reused selection/range data limit interpretation |
| Evidence-supported decisions | Slide 6: XGBoost (E1), rules (E3), quotes (E4), donor checks (E2), calibration (E5), rejection of fit as accuracy (E1/E5), and deferred neural/LLM comparison; dossier table links approaches, evidence, and decisions |
| Most important next question | Slide 6: train on some sites and test different sites; broader question: how would new development affect local water? |

E1-E5 match the dossier and [evidence table](evidence-summary.csv). E3 uses injected
outputs; E4 uses fictional permits. Neither is an LLM comparison.

## Rubric and timing

| Rubric category | Points | Coverage |
| --- | ---: | --- |
| Problem and map | 20 | Regional goal, users, current components, features/target/rules/vectors/metadata |
| Experiments and evidence | 25 | Model comparison, repeated missingness, coverage counts, clipping and geographic cases |
| Failure interpretation | 15 | Biased donors, interval shortfall, synthetic targets, proposed changes |
| Design and rationale | 20 | Decisions linked to E1-E5 on slide 6 |
| AI connections | 10 | Dossier explains how rules constrain learned trees, location metadata filters word-vector matches, gap filling changes model inputs, and coverage differs from prediction error; standalone map labels semantic representations |
| Presentation and questions | 10 | Six slides, four-minute talk, Q&A, three speaking roles |

Timing: 60 seconds for slides 1-2, 120 for slides 3-5, and 60 for slide 6.
Allow two more minutes for questions and transition.

## Submission components

| Component | Files |
| --- | --- |
| Curated dossier | `source/dossier.md`, `dossier.pdf`, selected `evidence/` files |
| Current system map | `semantic-system-map.svg`, `.png`, dossier diagram, slide 2 |
| Approach/evidence/decision summary | `evidence-summary.csv`, dossier decision table, slide 6 |
| Presentation | `review-slides-simplified.pptx`, `review-slides.pdf`, `presentation-script.md` |
| Individual contributions and speaking roles | `team-contributions.md`, `team-contributions.pdf`; two slides per member |

The assignment does not require a finished system, every class technique, or successful
results from every experiment. Dates, access, course references, and contribution status
are tracked in the [project checkoff](source/project-checkoff.md).
