# ECOllateral A2 review

The six-slide review explains the water-use prototype in plain language: four steps,
three tests, and the next step. The dossier is two pages and the talk takes about four minutes. Results use synthetic training targets
and station readings. The observed download tests parsing and units.

| Material | Contents |
| --- | --- |
| [Slides](review-slides-simplified.pptx) and [PDF](review-slides.pdf) | Editable presentation and preview |
| [Talk and Q&A](presentation-script.md) | Four-minute script and reference sheet |
| [Dossier](dossier.pdf) and [source](source/dossier.md) | Methods, results, and decisions |
| [Checkoff](project-checkoff.pdf) and [source](source/project-checkoff.md) | All 21 course items and outstanding actions |
| [System map](semantic-system-map.svg) and [PNG](semantic-system-map.png) | Number and permit paths |
| [Evidence summary](evidence-summary.csv) | Experiment and decision table |
| [Team responsibilities](team-contributions.md) | Assigned work and speaking roles |
| [Assignment coverage](assignment-coverage.md) | Requirements, rubric, and timing |

[Evidence files](evidence/README.md) retain the October 7 snapshot and source hashes
for implementation `125aa40`. Those hashes describe the original code. The earlier
development/export log remains in Git at `dbb9cf9:docs/implementation-notes.md`.

## Rebuild

Run from the repository root:

```powershell
.venv\Scripts\python -m pip install -e ".[materials]"
.venv\Scripts\python scripts/a2/build_materials.py
.venv\Scripts\python scripts/a2/collect_evidence.py --output data/processed/new-evidence
```

The builder exports dossier/checkoff PDFs and the SVG/PNG map. Intermediate files go
to ignored `data/processed/a2-build/`. The slides are edited in the PPTX and exported
separately. Charts use gallons per day or percentages. The gap chart shows the separate
bad-reading test; exact source values remain in the evidence CSVs. Capturing new
evidence leaves the dated dossier and slide figures unchanged.
