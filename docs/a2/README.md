# ECOllateral A2 review

Start with the slides or the talk below. The goal is to explain how development
changes water supply and rivers across an area. Cooling is one current example.
Current results use generated training examples. Next: collect real measurements,
train on them, and test on separate records and areas.

| File | Use it for |
| --- | --- |
| [review-slides-simplified.pptx](review-slides-simplified.pptx) | Editable presentation with simple speaker notes |
| [review-slides.pdf](review-slides.pdf) | Quick slide preview |
| [presentation-script.md](presentation-script.md) | Four-minute talk, Q&A, project guide, glossary |
| [dossier.pdf](dossier.pdf) | Full experiment results and limitations |
| [project-checkoff.pdf](project-checkoff.pdf) | Course checklist and pending actions |
| [semantic-system-map.svg](semantic-system-map.svg), [PNG](semantic-system-map.png) | Editable map and easy image preview |
| [evidence-summary.csv](evidence-summary.csv) | What we tested and what we decided |
| [team-contributions.md](team-contributions.md) | Team duties and contribution confirmation |
| [assignment-coverage.md](assignment-coverage.md) | Where every A2 requirement appears |

`evidence/` contains the original results and fingerprints needed to support claims.
`source/` contains editable dossier/checkoff text, data-source details, and export notes.
Build/capture scripts are in `../../scripts/a2/`.
The project goal and planned work are in `../project-scope.md`.

Before presenting, confirm the October 20/23 assignment, Submitty deadline, actual
contributions, course references, instructor access, and rehearsal. No submission
or access change has been performed. Generated results do not prove real-world accuracy.

## Rebuild materials

Run from the repository root with the project virtual environment:

```powershell
.venv\Scripts\python scripts/a2/collect_evidence.py
.venv\Scripts\python scripts/a2/build_materials.py
```

Evidence capture refreshes results, test logs, and fingerprints in `evidence/`;
see [the evidence guide](evidence/README.md) before replacing the historical snapshot.
Install `reportlab` and `pypdfium2` in the Python environment used for document exports. It exports the dossier,
checkoff, and SVG/PNG system map from `source/`.

Edit slides directly in `review-slides-simplified.pptx` and export their PDF in
PowerPoint. Chart workbooks round to ten significant digits; source CSVs retain full precision.
After rebuilding, reconcile quoted results, inspect each exported page, and update
`source/verification-notes.md`.
