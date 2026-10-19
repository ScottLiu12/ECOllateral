# A2 readiness review

Reviewed October 19, 2026. Experimental results remain the October 7 synthetic
snapshot; this review does not claim a new experiment or real-site validation.

| Requested improvement | Where to inspect |
| --- | --- |
| Explicit semantic representations | Slide 2 and standalone SVG/PNG: six numeric features, XGBoost learned trees, symbolic energy rules, TF-IDF vectors and HUC/location metadata |
| Evidence-to-decision summary | Dossier table and `evidence-summary.csv`: E1-E5 plus Reject and Defer decisions |
| Concrete failures | Slide 4 and dossier: biased donor 60% vs. interpolation 99% within tolerance; separate formula diagnostic; interpolation requires future observations |
| Uncertainty limitation | Slide 5 and dossier: 294/333 and 293/333 inside nominal 90% intervals; separate model selection and calibration next |
| Inspectable safeguards | Dossier E3: -1 -> 0 MGD and 1,000,000 -> 0.446484 MGD, with warning; E4: four named geographic cases in saved JSON |
| Decision rationale | Slide 6 links each adopted or modified component to E1-E5; neural/LLM comparisons deferred without a fair measured-data evaluation |
| Individual contributions | `team-contributions.md` gives one line per person; Shaun's coding is confirmed; Troy's and Scott's completed work still needs their confirmation |

## Team actions before submission

- Confirm Troy's and Scott's completed contributions; replace assigned work only
  with work they actually completed.
- Confirm whether the team presents October 20 or October 23, 2026 and check the
  posted Submitty deadline in the course system. Neither is verified here.
- Confirm instructor/TA access, exact class studio references, and office hours.
- Rehearse six slides in four minutes: slides 1-2 about 60 seconds, 3-5 about
  120 seconds, and slide 6 about 60 seconds; allow two minutes for questions.

Prepared files: dossier, six-slide editable deck and matching PDF, semantic map,
evidence table, contribution status, and presentation script. This is a mid-semester
review of cooling consumption; regional environmental impact remains future work.
