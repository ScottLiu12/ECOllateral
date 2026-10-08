# Data acquisition and governance

## Current sources

| Source | Exact acquisition / representation | Current evidence | Limits |
| --- | --- | --- | --- |
| USGS Water Data OGC API | `https://api.waterdata.usgs.gov/ogcapi/v1/collections/monitoring-locations/items` and `/daily/items`; HUC prefix and selected station ID | Two-day streamflow parser smoke run for USGS-01646500, HUC8 02070008 | Gauges represent point observations, not allocatable municipal supply |
| NOAA NCEI GSOD | `https://www.ncei.noaa.gov/access/services/data/v1`; `dataset=global-summary-of-the-day`, explicit station and dates | Two weather records for GSOD 72403093738, July 1-2, 2024 | Wet-bulb is a derived sea-level approximation, not an observed field |
| NOAA nClimDiv | `https://www.ncei.noaa.gov/monitoring-content/data/us/climdiv/monthly/current/`; newest `climdiv-pdsidv` file | Monthly PDSI parser and source filename | Smoke-test division 4401 is not spatially validated for the gauge/facility |
| Synthetic facility observations | Seeded generator in `src/demo.py`, 1,600 rows per cooling type | Regression benchmark and demo forecast | Invented consumption labels cannot establish field accuracy |
| Synthetic station series | 365 dates, target and two correlated neighbors | Missingness experiment | Random target gaps do not cover shared drought outages or nonrandom extremes |
| Permit sections | Operator-supplied JSONL with section, source URL, HUC or coordinate radius | Fictional `example.org` fixtures | No verified EPA/EIA/municipal corpus has been indexed yet |

Ingestion retains units, station identity, USGS status/qualifiers, NOAA attributes, and
source periods. CSV snapshots preserve missing observations; the model imputes only
flow/PDSI from training statistics. Source quality flags are retained but are not yet
used to reject all provisional or estimated readings in automated forecasting.

## Access and rights checks

The current workflow reads documented public APIs and NOAA's public bulk-file catalog.
It does not use login bypass, private accounts, commercial scraping, or human surveys.
USGS's [API landing page](https://api.waterdata.usgs.gov/) and
[data-licensing guidance](https://www.usgs.gov/data-management/data-licensing) describe
US-government data and distinguish third-party material. NOAA's
[education FAQ](https://www.noaa.gov/office-education/outreach-communication/faq) describes
NOAA data as public domain and permits outside organizations to build applications.
These provider statements were consulted on October 7, 2026; retain provenance and
check product-specific notices when assembling a new corpus.

This check applies to the public environmental data used here. It does not establish
rights to every third-party item linked by an agency, every municipal permit compilation,
or copyrighted ASHRAE handbook text. The project cites ASHRAE guidance and uses its own
engineering implementation; it does not distribute a copied handbook.

No survey or interview data are part of this snapshot. Before adding user studies,
confirm the course/institution's IRB requirements with the instructor. Before adding
HTML scraping beyond documented data catalogs or a new permit source, confirm access
and redistribution terms and the course's approval expectations. No instructor approval
or IRB determination is claimed in these materials.

## Responsible interpretation

The model estimates on-site cooling consumption. It excludes grid water use, domestic
water, return-flow accounting, other withdrawals, and ecological minimum flows.
Its field named `predicted_collateral_stress_mgd` is a compatibility label, not a
validated municipal water-stress index. Retrieve permit language as context for human
review; do not turn a retrieved passage into an automated compliance finding.

## Evidence provenance

`evidence/manifest.json` records the implementation snapshot commit, the evidence capture
commit, Python version, seed, and SHA-256 hashes for source files and selected outputs.
The implementation snapshot predates these course-documentation commits. Raw data and
serialized model artifacts remain in ignored directories; the dossier uses selected
portable outputs. The original course PDFs remain unchanged in the user's Downloads.
