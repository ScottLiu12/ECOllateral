# CSCI 4150 A2: ECOllateral evidence review

Prepared against the supplied Fall 2026 project checkoff and A2 brief. This package
reviews the implemented research prototype and its evidence, with explicit limits on
synthetic validation. Presentation day is pending: October 20 or October 23, 2026.
The exact Submitty deadline is not supplied in the brief.

## Deliverables

- `dossier.md` and `dossier.pdf`: curated project problem, semantic map, experiments,
  limitations, decisions, next question, and team contribution snapshot.
- `project-checkoff.md` and `project-checkoff.pdf`: every project checklist item, its
  evidence, and remaining human/course actions.
- `semantic-system-map.svg` and `.png`: readable component and representation map.
- `evidence-summary.csv`: tested approach, hypothesis, evidence, decision, and implication.
- `review-slides.pptx` and `review-slides.pdf`: six-slide evidence review.
- `presentation-script.md`: four-minute script, slide timing, team handoffs, and Q&A.
- `team-contributions.md`: Shaun, Troy, and Scott's responsibilities and accountability.
- `data-governance.md`: public sources, provenance, rights references, and access limits.
- `requirements-map.md`: A2 requirements and grading criteria mapped to the package.
- `evidence/`: portable benchmark tables, forecast output, failure cases, research charts,
  test output, source metadata, and checksums. No serialized model is included.

Open `dossier.pdf` for the review and `review-slides.pptx` for presentation editing.
The Markdown and CSV files remain editable. `build_materials.py` and `build_slides.mjs`
record how the exports were made; `collect_evidence.py` refreshes inspectable evidence.

## Scope of the evidence

The regression and missingness metrics use synthetic facility labels and synthetic
hydrology. Live public ingestion only verifies connectivity, parsing, and units.
Fictional permit sections test retrieval mechanics and cannot establish compliance.
AI approaches investigated in the repository include symbolic constraints, tabular ML,
time/spatial interpolation, and TF-IDF/FAISS retrieval. Neural models and generative LLM
summaries have not been tested. The actual class studio roster was not supplied.

## Before submitting

- Confirm the presentation day and Submitty deadline with the course.
- Verify instructor/TA GitHub access; the configured remote alone does not prove access.
- Schedule office hours and rehearse questions with all three team members.
- Review assigned responsibilities and record actual completed contributions.
- Confirm studio-specific references and any intended future scraping or survey work.

The attached documents provide assignment requirements. They do not authorize course
submission, external messages, repository permission changes, or invented team activity.
