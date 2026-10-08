# Validation results — 2026-10-07

These checks ran locally on Windows with Python 3.12.14. They show the prototype works
and handles its test cases. They do not establish accuracy at real facilities or whether
a permit legally applies. Plain-English definitions are in `a2/explain-it-simply.md`.

ECOllateral's purpose is to assess regional ecosystem impacts from development. The
results below test the current environmental-data/cooling-pressure components; they
do not validate area-wide municipal reserve or watershed-stress predictions. See
`project-scope.md` for that distinction and the regional validation still required.

## Checks

| Check | Result |
| --- | --- |
| `python -m pytest -q` | 51 passed; one upstream Starlette/httpx deprecation warning |
| `python -m ruff check src tests scripts` | Passed |
| `python -m ruff format --check src tests scripts` | Passed, 30 files |
| `npm run typecheck` | Passed |
| `python -m src.cli demo` | Completed, synthetic artifacts saved |
| `python scripts/run_notebook.py` | Completed; tables, plots, executed notebook saved |
| Two-day USGS + NOAA ingestion | Completed against public endpoints |
| GitHub Actions | Configured locally; not run remotely |

The small real-data download/parsing check used USGS-01646500 in verified HUC8 02070008,
NOAA GSOD station 72403093738, and July 1–2, 2024. It saved two streamflow records,
two weather records, and one monthly environmental snapshot. The selected climate
division 4401 tested only PDSI parsing; its location match was not validated.
Source files remain in ignored `data/raw/live-smoke` and `data/processed/live-smoke`.

## Model comparison using made-up data

Each cooling technology has 1,600 generated records across six years. Train both models
on the oldest 60% of dates. Choose using RMSE on the next 20%; RMSE gives large errors
extra weight. Test on the newest 20%. This table shows test predictions after physical
limits are applied. MAE is average error size; R² measures fit. `src/demo.py` generates
the synthetic targets; they are not measured water use.

| Cooling technology | Selected model | Held-out R² | MAE, MGD | RMSE, MGD | Nominal 90% interval coverage |
| --- | --- | ---: | ---: | ---: | ---: |
| Cooling tower | XGBoost | 0.99808 | 0.003668 | 0.004583 | 88.29% |
| Direct evaporative | XGBoost | 0.99728 | 0.003191 | 0.004048 | 87.99% |
| Dry air cooled | RandomForest | Undefined | 0.000000 | 0.000000 | 100.00% |

Both evaporative models meet R² > 0.80 and MAE < 0.05 MGD on these generated targets.
Their prediction ranges include **less** than the intended 90% of test values. This is
a finite sample, with no statistical significance test. R² is not the probability a
prediction is right. Intended 90% coverage is not verified 90% coverage at real facilities.
Dry cooling has a constant zero target in our scope, so R² is undefined.

The next 20% of dates currently does two jobs: choosing the model and setting its
prediction range. Separate those jobs in the next evaluation (A2 investigation E5).

Scores for each model before/after limits, split dates, row counts, and range radii are
in `data/processed/demo/benchmark.json` and reproduced by `python -m src.cli demo`.

## Missing drought readings using made-up station data

The notebook used 365 dates, including 121 drought dates, with 50 repeat runs per gap
rate. A fixed random seed makes the runs repeatable. Both methods lose the same
readings in each repeat: one fills from nearby stations, the other uses a straight line
between readings around a gap. Variance measures how much the predictions change.

| Removed drought records | Records removed per replicate | Spatial prediction variance, MGD² | Linear prediction variance, MGD² |
| --- | ---: | ---: | ---: |
| 10% | 12 | 3.295e-9 | 6.001e-9 |
| 25% | 30 | 6.314e-9 | 2.212e-8 |
| 40% | 48 | 9.054e-9 | 4.092e-8 |

All six comparisons kept 100% of drought prediction changes within ±0.05 MGD. Every
central 90% change band also stayed inside that limit. The made-up stations behave
similarly, and the fitted model changes only modestly with flow. This does not validate
filling gaps during real droughts. Other tests deliberately bias neighboring stations
and show that the analysis can flag instability. These change bands are not prediction
intervals for future consumption.

The separate made-up groundwater test keeps depth in meters. Spatial MAE ranges from
0.0113 to 0.0127 m; temporal MAE ranges from 0.000160 to 0.000385 m. No groundwater
depth is treated as an MGD model input.

Notebook outputs are in `data/processed/research/`: `missingness_summary.csv`,
`missingness_bands.csv`, `groundwater_reconstruction.csv`, two PNG figures, and
`missingness.executed.ipynb`. Both figures were inspected for readable units, legends,
drought labeling, and tolerance bounds. The tracked source notebook remains unexecuted
so generated images and machine-specific paths do not bloat Git history.

## Remaining field work

- Collect independently measured facility water use, checked station matches, cooling
  setup, utilization, and PUE measurements.
- Test on whole facilities and drought periods not used for training. Check range
  coverage, multiple stations failing together, and long blocks of missing readings.
- Add real, checked permit sections with explicit location coverage.
- Establish a measured groundwater-to-flow relationship before using filled groundwater
  readings to test changes in water-use predictions.
- Check which water uses the model includes before describing town-wide stress.
  Allocation, return flows, ecological needs, and other withdrawals are not modeled.
