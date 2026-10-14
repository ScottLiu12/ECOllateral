# Implementation notes

## Application

The CLI downloads observations, trains models, indexes extracted permit sections, and
runs the missingness experiment. FastAPI loads local artifacts and combines a monthly
environmental snapshot, a bounded prediction, and eligible permit quotations.
`src/api/app.py` contains the endpoint and its schemas. Feature preparation and training
are in `src/models/regression.py`; retrieval and summaries are in `src/grounding/store.py`.
There is no external embedding or language-model service.

## Physical and modeling choices

- Capacity is IT power. Thermal energy is `MW × 1000 × 24 × utilization × PUE`.
  The evaporation ceiling uses `3600 / (2501 - 2.361 × max(wet_bulb_c, 0))` liters
  per thermal kWh, adjusted by the maximum evaporative fraction. Divide by
  3,785,411.784 liters per million US gallons to obtain MGD.
- Both evaporative technologies use this screening ceiling. Zero is the lower bound;
  dry air cooling excludes evaporative assistance. Defaults are assumptions, not
  universal ASHRAE limits. Freezing and low wet-bulb depression produce warnings.
- Train RandomForest and XGBoost separately for each cooling type. Entire dates stay
  together in chronological 60/20/20 training, calibration, and test partitions.
  Only training data fit the median imputer. Flow and PDSI can be missing.
- Select by calibration RMSE. Absolute bounded calibration errors set the nominal
  90% range, using a finite-sample quantile. Reusing calibration data for selection
  and range sizing is a known limitation; time dependence also weakens coverage claims.
- Preserve raw predictions and flag physical clipping, missing inputs, extrapolation,
  and synthetic models. R² is undefined for constant targets and is not confidence.
  Synthetic accuracy and sensitivity results do not validate real facilities.
- Keep artifact classes in their original modules so existing joblib files load.
  Only load trusted local artifacts; pickle/joblib can execute code.

## Environmental data and permit context

USGS daily means retain station IDs and quality flags. Flow converts from cfs using
0.64631688969744 MGD/cfs; levels convert feet to meters. Negative groundwater depth
can be valid. Pagination has a page limit, loop detection, and a host check before
forwarding credentials. HTTP failures are not empty datasets.

NOAA GSOD temperature and dew point estimate wet-bulb using Stull's sea-level equation.
Out-of-domain estimates become missing; saturation uses wet-bulb = dry-bulb. PDSI comes
from the latest listed nClimDiv file. A climate division must be selected separately
from a HUC. Monthly medians describe historical scenarios, not future weather.
Coordinate lookup uses a configured station within 50 km and labels the approximation.

TF-IDF/FAISS ranks section text. HUC or explicit coordinate-radius eligibility is checked
before selecting top-k. Citations retain exact text and source offsets. The summary
quotes permit numbers without interpreting them or deciding legal compliance.

## Missingness study

Mask only observed drought readings, using the same seeded masks for both methods.
Spatial filling tries same-day donors in distance order; linear interpolation uses
elapsed time and can use future observations. Report variance and 5th/95th percentile
change bands separately from forecast intervals. Groundwater reconstruction stays in
meters and needs a measured relationship before it can represent streamflow.
See [data contracts](data-contracts.md) for file schemas and [validation results](validation-results.md)
for the dated measurements and remaining field work.

## References

- [ASHRAE data centers and WUE](https://handbook.ashrae.org/Handbooks/A23/SI/A23_Ch20/a23_ch20_si.aspx)
- [ASHRAE cooling towers](https://handbook.ashrae.org/Handbooks/S24/IP/s24_ch40/s24_ch40_ip.aspx)
- [USGS OGC API](https://api.waterdata.usgs.gov/docs/ogcapi/) and [migration fields](https://api.waterdata.usgs.gov/docs/ogcapi/migration/)
- [NOAA data service](https://www.ncei.noaa.gov/access/search/documentation/data-service/) and [GSOD](https://www.ncei.noaa.gov/access/search/datasets/global-summary-of-the-day/)
- [NOAA nClimDiv](https://www.ncei.noaa.gov/pub/data/cirs/climdiv/)
- [Stull (2011)](https://doi.org/10.1175/JAMC-D-11-0143.1)

The detailed development/export log is retained in Git:
`git show dbb9cf9:docs/implementation-notes.md`. The October 7 evidence manifest and
original result files remain unchanged.
