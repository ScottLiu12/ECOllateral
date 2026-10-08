# Data sources, permissions, and limits

## Current sources

| Source | Exact download / format | Evidence we have | What it does not show |
| --- | --- | --- | --- |
| USGS Water Data OGC API | `https://api.waterdata.usgs.gov/ogcapi/v1/collections/monitoring-locations/items` and `/daily/items`; HUC prefix and chosen station ID | Two-day river-flow parsing check: USGS-01646500, HUC8 02070008 | A gauge measures one place; it does not show how much water a town can allocate |
| NOAA NCEI GSOD | `https://www.ncei.noaa.gov/access/services/data/v1`; `dataset=global-summary-of-the-day`, chosen station and dates | Two weather readings: GSOD 72403093738, July 1-2, 2024 | Wet-bulb temperature is estimated using a sea-level approximation, not directly measured |
| NOAA nClimDiv | `https://www.ncei.noaa.gov/monitoring-content/data/us/climdiv/monthly/current/`; newest `climdiv-pdsidv` file | Monthly drought-score (PDSI) parser and source filename | Division 4401's location match to the gauge/facility is not validated |
| Made-up facility observations | Fixed-seed generator in `src/demo.py`, 1,600 rows per cooling type | Model comparison and demo forecast | Generated water-use targets cannot prove real-facility accuracy |
| Made-up station readings | 365 dates, a target and two similar neighbors | Missing-data experiment | Random target gaps do not cover multiple stations failing together or extreme readings being more likely to disappear |
| Permit sections | User-supplied JSONL: section, source URL, HUC or coordinate radius | Fictional `example.org` test documents | No real, checked EPA/EIA/municipal collection has been added to search yet |

Downloads keep units, station IDs, USGS status/qualifiers, NOAA attributes, and source
dates. Saved CSVs keep gaps visible. The model fills only flow/PDSI gaps using training
statistics. Quality flags remain attached, but the forecast does not yet automatically
reject every provisional or estimated reading.

## Access and rights checks

The current workflow uses documented public APIs and NOAA's public bulk-file catalog.
It does not bypass logins, use private accounts, scrape commercial sites, or survey people.
USGS's [API landing page](https://api.waterdata.usgs.gov/) and
[data-licensing guidance](https://www.usgs.gov/data-management/data-licensing) describe
US-government data and distinguish third-party material. NOAA's
[education FAQ](https://www.noaa.gov/office-education/outreach-communication/faq) describes
NOAA data as public domain and permits outside organizations to build applications.
These provider statements were checked on October 7, 2026. Keep source information and
check each product's notices when building a new data or document collection.

This check covers the public environmental data used here. It does not establish rights
to every third-party item linked by an agency, municipal permit collection, or copyrighted
ASHRAE handbook passage. The project cites ASHRAE and implements its own engineering
rules. It does not distribute a copied handbook.

There are no survey or interview data in this snapshot. Before studying people, ask the
instructor about course/institutional IRB requirements. Before scraping HTML outside
documented data catalogs or adding a permit source, check access/sharing terms and course
approval expectations. These materials do not claim instructor approval or an IRB decision.

## What the result means

The goal is to assess development impacts on seasonal area reserves and watershed
conditions. Regional balances and ecological thresholds still need observed data and
validation; see `../../project-scope.md`.

The model estimates on-site cooling water use. It excludes water used to generate grid
electricity, domestic water, return-flow accounting, other withdrawals, and ecological
minimum flows. The existing field `predicted_collateral_stress_mgd` keeps a compatible
API name; it is not a validated town-wide water-stress score. Permit text gives context
for a person to review. A matching passage is not an automated compliance finding.

The supplied context proposes EIA/EPA profiles, environmental impact statements, and
regional assessments. Those collections have not been ingested or validated here.
Groundwater depth is not recharge. Historical recharge and heatwave studies remain
planned. Check the actual sources' access and rights when selecting those products.

## How to trace the evidence

`../evidence/manifest.json` records the implementation commit, evidence-capture commit,
Python version, random seed, and SHA-256 file fingerprints. Fingerprints let us detect
changes to source files and selected results. The implementation snapshot is older than
the course-document commits. Raw data and saved model objects remain in ignored folders;
the dossier includes selected portable results. The original course PDFs in Downloads
remain unchanged.
