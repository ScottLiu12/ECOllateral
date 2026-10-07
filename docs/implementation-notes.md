# Implementation notes

## 2026-10-07 — Scope and repository setup

- Starting point: `main`, three README-only commits, no application or existing tests.
  Remote: `https://github.com/ScottLiu12/ECOllateral.git`.
- The brief requests Python ingestion, physical bounds, tabular regression, drought
  missingness experiments, permit retrieval, and a FastAPI endpoint. Keep the requested
  directories at the repository root; the checkout is already named ECOllateral.
- Use a small typed TypeScript HTTP client for downstream consumers; no frontend is
  specified. Avoid introducing a UI or LLM orchestration framework.
- Commit each coherent piece, with notes updated at the same time. Local commits are
  authorized by the user. No push or deployment is requested.
- First commit: package metadata, Make commands, importable modules, ignored runtime
  artifacts, and development instructions.
- The sandbox marks `.git` read-only, so local Git writes require tool escalation.
  The first authorized escalation succeeded. No GitHub credentials were needed.
- The Microsoft Store Python launcher was inaccessible inside the sandbox. Inspect
  the bundled runtime before choosing a working local environment.

## Research and modeling decisions

- ASHRAE's data-center handbook defines WUE as liters of site water per kWh of IT
  energy. It does **not** establish universal per-technology WUE or PUE limits.
  Physical screening must distinguish this definition from liters per thermal kWh.
- Use an explicit heat-balance envelope, with capacity defined as IT power, configurable
  utilization and PUE. The evaporative ceiling uses latent heat of vaporization. Zero
  is the conservative lower bound because hybrid operation and heat reuse can avoid
  evaporation. Air-cooled means dry heat rejection without adiabatic assist.
- Scope of the target: daily on-site cooling consumption, excluding grid water use,
  domestic uses, and tower blowdown returned to the watershed. A municipal water-stress
  assessment needs more hydrology and allocation data than the six requested features.
- Train separate models by cooling technology because cooling type is absent from the
  required six-feature matrix. Do not pool unlike facilities and then rely on clipping
  to repair an ambiguous target.
- Report held-out R² as a fit metric, never as a probability or confidence interval.
  A synthetic benchmark can test mechanics but cannot validate real-world accuracy.
- USGS provides modern OGC REST collections. Discover sites by HUC, then query daily
  streamflow (`00060`), gauge height (`00065`), and groundwater depth (`72019`) by site.
  Retain station identity and quality flags; do not add gauges together as basin supply.
- NOAA GSOD supplies temperature, dew point, and precipitation, not PDSI or observed
  wet-bulb. Derive approximate RH/wet-bulb with an explicit validity range; use monthly
  nClimDiv PDSI with a separately supplied climate-division ID. HUCs and NOAA divisions
  are different geographies and must not be treated as interchangeable.
- Grounding will use FAISS over local TF-IDF vectors, without an embedding service or
  download. Restrict excerpts by geography before ranking. Narratives quote indexed
  text and format the already calculated forecast; they perform no risk arithmetic.

### Primary references consulted

- [ASHRAE data centers, WUE definition](https://handbook.ashrae.org/Handbooks/A23/SI/A23_Ch20/a23_ch20_si.aspx)
- [ASHRAE cooling-tower heat transfer](https://handbook.ashrae.org/Handbooks/S24/IP/s24_ch40/s24_ch40_ip.aspx)
- [USGS OGC getting started](https://api.waterdata.usgs.gov/docs/ogcapi/)
- [USGS migration and field names](https://api.waterdata.usgs.gov/docs/ogcapi/migration/)
- [NOAA Access Data Service](https://www.ncei.noaa.gov/access/search/documentation/data-service/)
- [NOAA GSOD dataset](https://www.ncei.noaa.gov/access/search/datasets/global-summary-of-the-day/)
- [NOAA nClimDiv files](https://www.ncei.noaa.gov/pub/data/cirs/climdiv/)
- [Stull (2011), wet-bulb approximation](https://doi.org/10.1175/JAMC-D-11-0143.1)

### Validation plan

Test conversions and bounds at zero/large loads, invalid psychrometric inputs,
ingestion pagination and missing-value sentinels, training without preprocessing
leakage, raw and clipped predictions, drought-only masks at all requested rates,
nearest-station fallback, interval coverage, geographic citation filtering, artifact
reload, and the offline ingestion-to-API pipeline. Execute the notebook and type-check
the client once the core passes. Keep external-service checks separate from offline
tests, and record failures or unverified behavior rather than inventing results.
