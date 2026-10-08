# Inspectable evidence snapshot

Captured October 7, 2026 from implementation `125aa40`. `manifest.json` records exact
source and evidence SHA-256 hashes, seed, Python version, and capture commit.

| ID | Files | What the evidence establishes |
| --- | --- | --- |
| E1 | regression-comparison.csv, benchmark.json | RF/XGB comparison and selection on synthetic labels |
| E2 | missingness-summary.csv, missingness-sensitivity.png, missingness-band90.png | Fitted-model perturbation from random drought gaps |
| E2 diagnostic | biased-donor-diagnostic.csv | Donor-bias exposure using a separate simple predictor |
| E3 | constraint-failure-cases.json | Intentionally injected impossible predictions are clipped and flagged |
| E4 | retrieval-cases.json | Four geography/lexical cases in a fictional permit corpus |
| E5 | interval-coverage.csv | Held-out synthetic coverage below nominal for evaporative models |
| API | forecast-request.json, forecast.json | Persisted artifacts load and a request produces flagged/cited output |
| Ingestion | live-ingestion-snapshot.csv | Two-day public-source parsing smoke test; climate geography unverified |
| Separate research | groundwater-reconstruction.csv | Reconstruction error in meters, not consumption in MGD |
| Tests | test-results.txt | Local suite: 51 passing tests and one upstream deprecation warning |

Refresh from the repository root with:

```powershell
.venv\Scripts\python.exe docs\a2\collect_evidence.py
```

The script uses local synthetic benchmark/research artifacts and the preserved live
smoke snapshot. If those ignored artifacts are absent, first follow the demo, training,
sensitivity, and ingestion instructions in the project README and validation notes.
It is a snapshot collector, not an external data acquisition or submission command.

After refreshing, reconcile the rounded dossier/slide figures and regenerate the
exports. The evidence manifest covers the captured inputs/results; it does not hash
itself or claim that slides are automatically updated. No pickled model is distributed
in the dossier. Source code remains the repository authority for behavior.
