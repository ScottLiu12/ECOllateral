# ECOllateral

Ecosystem Collateral Forecast Tool. Estimates daily on-site cooling water consumption
in million US gallons per day (MGD), constrains predictions with an engineering heat
balance, and attaches local regulatory excerpts.

The regression target is cooling water consumption. Assessing municipal water stress
also requires supply, other withdrawals, return flows, and ecological flow requirements.

## Development

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m pytest
```

On systems with Make, `make lint`, `make test`, `make run`, and `make ingest ARGS="..."`
wrap the same Python commands. Ingestion, training, and API examples are added alongside
their implementation.
