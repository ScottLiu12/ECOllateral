# A2 document and evidence scripts

Run from the repository root.

- `collect_evidence.py` refreshes experiment results, the test log, and fingerprints
  in `docs/a2/evidence/`. Use the project virtual environment; details are in
  `../../docs/a2/evidence/README.md`.
- `build_materials.py` exports the dossier, checkoff, and SVG/PNG system map from
  `docs/a2/source/`. It needs Python with `reportlab` and `pypdfium2` installed.

```powershell
python scripts/a2/build_materials.py
```

The PDF builder includes a slide PDF when reviewed PNGs are present in
`data/processed/a2-build/slides/final-render/`. For presentation changes, edit the
native text, diagram, or charts in `docs/a2/review-slides-simplified.pptx`, then
export that deck to `docs/a2/review-slides.pdf` in PowerPoint. Refresh or remove old
slide PNGs before running the PDF builder so it cannot reuse outdated previews.

Chart workbooks round to ten significant digits; source CSVs keep full precision.
Reconcile quoted numbers after new experiments, inspect every exported page, and
update `docs/a2/source/verification-notes.md`. The reviewed files in `docs/a2/`
are the handoff; no duplicate ZIP is generated.
