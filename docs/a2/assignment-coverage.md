# A2 assignment coverage

Based on the supplied two-page `CSCI 4150 Project Checkoff List.pdf` and three-page
`CSCI4150_A2_MidSemester_System_Evidence_Review.pdf`.

## Required presentation content

| Requirement | Slides and supporting evidence |
| --- | --- |
| Problem, users, and setting | Slide 1: seasonal development impacts for planners, researchers, and utilities; cooling consumption is the current component |
| Current semantic/system map | Slide 2: six features, tree models, physical rules, word vectors, source/location metadata, and quotations; standalone SVG/PNG |
| At least three meaningful investigations | E1 model comparison (3), E2 gap filling (4), E5 range coverage (5); E3/E4 safeguards on slide 2 |
| Inspectable evidence | Editable charts on slides 3-5; CSV/JSON source footers; methods, units, and sample counts in notes and dossier |
| Consequential failure or limitation | Slide 4: biased donors; slide 5: 88.3%/88.0% coverage versus 90%; synthetic labels and shared selection/calibration data limit interpretation |
| Evidence-supported decisions | Slide 6: Adopt models/limits/location checks, Modify missingness/ranges, Reject R2-as-confidence and regional claims, Defer neural/LLM comparisons |
| Most important next question | Slide 6: can measured conditions and development demand support a seasonal assessment in an unseen area? |

E1-E5 match the dossier and [evidence table](evidence-summary.csv). E3 uses injected
outputs; E4 uses fictional permits. Neither is an LLM comparison.

## Rubric and timing

| Rubric category | Points | Coverage |
| --- | ---: | --- |
| Problem and map | 20 | Regional goal, users, current components, features/target/rules/vectors/metadata |
| Experiments and evidence | 25 | Model comparison, repeated missingness, coverage counts, clipping and geographic cases |
| Failure interpretation | 15 | Biased donors, interval shortfall, synthetic targets, proposed changes |
| Design and rationale | 20 | Decisions linked to E1-E5 on slide 6 |
| AI connections | 10 | Supervised trees, symbolic rules, word vectors, metadata filtering, interpolation, uncertainty tests |
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
| One line per teammate | `team-contributions.md` |

The assignment does not require a finished system, every class technique, or successful
results from every experiment. Dates, access, course references, and contribution status
are tracked in the [project checkoff](source/project-checkoff.md).
