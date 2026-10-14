# Project scope

ECOllateral asks how proposed development affects seasonal municipal water reserves
and watershed conditions. Intended users are municipal planners, environmental
researchers, and utilities.

## Course prototype

The current implementation estimates one development pressure: daily on-site cooling
consumption. It downloads USGS/NOAA data, builds monthly conditions, compares two tree
models, applies physical limits, retrieves geographically eligible permit quotations,
and tests sensitivity to missing drought readings. A local CLI, API, notebook, and
small TypeScript client are enough to demonstrate that pipeline.

The model uses synthetic facility targets and the research experiment uses synthetic
station series. The two-day observed download checks parsing and units. Neither
validates regional reserves or ecosystem health. The existing API field
`predicted_collateral_stress_mgd` continues to mean on-site cooling consumption.

## Work needed for an area assessment

- Verify watershed/utility boundaries, station matches, and long observed histories.
- Collect measured development demand, other withdrawals, returns, and supply/reserves.
- Define ecological flow needs and measured regional outcomes before training a stress model.
- Train on measured facility consumption and test unseen facilities, areas, seasons,
  and drought periods. Separate model selection from range calibration.
- Add checked real permits and review retrieval relevance and legal applicability.

Groundwater depth is not recharge. Regional balances, historical recharge/heatwave
studies, neural models, dense embeddings, and generative/zero-shot LLM comparisons
remain future work. Do not describe them as completed experiments.

See [validation results](validation-results.md) for component evidence and the
[A2 package](a2/README.md) for review materials, assignment coverage, and team duties.
