# Evidence files: what each one shows

Captured October 7, 2026 from implementation `125aa40`. `manifest.json` records exact
source/result fingerprints (SHA-256), random seed, Python version, and capture commit.
Source hashes describe that original implementation, not the refactored source.

The experiments use synthetic cooling targets and station readings. The observed
snapshot tests parsing and units. The [project README](../../../README.md) describes
the regional assessment still to build.

| ID | Files | What the evidence establishes |
| --- | --- | --- |
| E1 | regression-comparison.csv, benchmark.json | Compare RF/XGB and choose a model using made-up water-use targets |
| E2 | missingness-summary.csv, missingness-sensitivity.png, missingness-band90.png | How the trained model's predictions change after random drought gaps |
| E2 diagnostic | biased-donor-diagnostic.csv | A separate simple formula shows why biased neighbors can hurt gap filling |
| E3 | constraint-failure-cases.json | Deliberately impossible numbers are moved to physical limits and flagged |
| E4 | retrieval-cases.json | Four word/location checks using made-up permits |
| E5 | interval-coverage.csv | Prediction ranges miss their coverage goal on saved synthetic test data |
| API | forecast-request.json, forecast.json | Saved model files load and a request returns warnings and source quotations |
| Ingestion | live-ingestion-snapshot.csv | Two-day public-data parsing check; climate location match unverified |
| Separate research | groundwater-reconstruction.csv | Gap-filling error in meters, separate from water use in MGD |
| Tests | test-results.txt | Local suite: 51 passing tests and one upstream deprecation warning |

Capture a new snapshot without replacing the historical results:

```powershell
.venv\Scripts\python.exe scripts\a2\collect_evidence.py --output data/processed/new-evidence
```

The capture script trains a fresh synthetic demo and records model, missingness,
clipping, retrieval, API, and test results. An existing observed download may be
included as a parser example. Historical plots and groundwater tables remain in this
folder; they are not copied into new captures.

New captures default to ignored `data/processed/new-evidence/`. Use an explicit
`--output docs/a2/evidence` to replace the historical tables and manifest. Capturing
results does not update quoted figures or exported course materials.
