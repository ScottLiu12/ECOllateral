# Evidence files: what each one shows

Captured October 7, 2026 from implementation `125aa40`. `manifest.json` records exact
source/result fingerprints (SHA-256), random seed, Python version, and capture commit.

These are component tests for a regional ecosystem impact project. Cooling-water
results measure one development pressure. No regional reserve balance, ecosystem
health score, zero-shot LLM benchmark, or groundwater recharge forecast is validated
by this evidence. See `../../project-scope.md` for the regional goal and remaining work.

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

Refresh from the repository root with:

```powershell
.venv\Scripts\python.exe docs\a2\collect_evidence.py
```

The script uses local made-up benchmark/research results and the saved real-data
download example. If those ignored files are missing, first follow the demo, training,
missing-data, and download commands in the project README and validation notes.
This collects a local evidence snapshot. It does not fetch external data or submit coursework.

After refreshing, check rounded figures in the dossier/slides and rebuild the exports.
The manifest fingerprints the captured inputs/results, not itself. Updating evidence
does not automatically update the slides. The dossier does not distribute pickled
model objects. The repository's source code defines the software's actual behavior.
