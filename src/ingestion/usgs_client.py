import re
from datetime import date
from typing import Any

import httpx
import numpy as np
import pandas as pd

BASE_URL = "https://api.waterdata.usgs.gov/ogcapi/v1"
CFS_TO_MGD = 0.64631688969744
PARAMETERS = {"00060": "streamflow_mgd", "00065": "gauge_height_m", "72019": "groundwater_depth_m"}
OBSERVATION_COLUMNS = [
    "date",
    "station_id",
    "huc8",
    "parameter_code",
    "value",
    "unit",
    "latitude",
    "longitude",
    "quality",
]


def _items(
    client: httpx.Client, collection: str, params: dict[str, str], api_key: str | None
) -> list[dict[str, Any]]:
    headers = {"X-Api-Key": api_key} if api_key else {}
    url = f"{BASE_URL}/collections/{collection}/items"
    query: dict[str, str] | None = {"f": "json", "limit": "1000", **params}
    features = []
    seen = set()
    for _ in range(1000):
        response = client.get(url, params=query, headers=headers)
        response.raise_for_status()
        payload = response.json()
        features.extend(payload["features"])
        next_url = next(
            (link["href"] for link in payload.get("links", []) if link["rel"] == "next"), None
        )
        if not next_url:
            return features
        next_url = str(response.url.join(next_url))
        # Do not forward API credentials to a host supplied by a pagination response.
        if httpx.URL(next_url).host != httpx.URL(BASE_URL).host or next_url in seen:
            raise ValueError("invalid USGS pagination link")
        seen.add(next_url)
        url, query = next_url, None
    raise ValueError("USGS pagination exceeded 1000 pages; narrow the date window")


def fetch_huc_observations(
    client: httpx.Client,
    huc8: str,
    start: date,
    end: date,
    *,
    api_key: str | None = None,
    station_ids: tuple[str, ...] | None = None,
) -> pd.DataFrame:
    if len(huc8) != 8 or not huc8.isascii() or not huc8.isdigit():
        raise ValueError("huc8 must be eight digits, including leading zeros")
    if end < start:
        raise ValueError("end must be on or after start")
    scope = f"hydrologic_unit_code LIKE '{huc8}%' AND agency_code = 'USGS'"
    if station_ids is not None:
        if not station_ids or any(
            not re.fullmatch(r"USGS-[0-9]{8,15}", station) for station in station_ids
        ):
            raise ValueError("station_ids must contain USGS station identifiers")
        scope += " AND id IN (" + ",".join(f"'{station}'" for station in station_ids) + ")"
    sites = _items(
        client,
        "monitoring-locations",
        {
            "filter": scope,
            "filter-lang": "cql2-text",
        },
        api_key,
    )
    rows = []
    for site in sites:
        properties = site["properties"]
        if not str(properties.get("hydrologic_unit_code", "")).startswith(huc8):
            continue
        station_id = properties["id"]
        coordinates = (site.get("geometry") or {}).get("coordinates", [np.nan, np.nan])
        for parameter in PARAMETERS:
            observations = _items(
                client,
                "daily",
                {
                    "monitoring_location_id": station_id,
                    "parameter_code": parameter,
                    "statistic_id": "00003",
                    "datetime": f"{start.isoformat()}/{end.isoformat()}",
                },
                api_key,
            )
            for feature in observations:
                observation = feature["properties"]
                raw = observation.get("value")
                value = float(raw) if raw not in (None, "") else np.nan
                if value <= -999 or not np.isfinite(value):
                    value = np.nan
                unit = observation["unit_of_measure"]
                if parameter == "00060":
                    if unit not in ("ft^3/s", "ft3/s"):
                        raise ValueError(f"unexpected streamflow unit: {unit}")
                    value = value * CFS_TO_MGD if value >= 0 else np.nan
                    output_unit = "MGD"
                else:
                    if unit != "ft":
                        raise ValueError(f"unexpected water-level unit: {unit}")
                    value *= 0.3048
                    output_unit = "m"
                status = observation.get("approval_status", observation.get("approvals_status"))
                qualifiers = observation.get("qualifier")
                if isinstance(status, list):
                    status = ";".join(status)
                if isinstance(qualifiers, list):
                    qualifiers = ";".join(qualifiers)
                rows.append(
                    {
                        "date": observation["time"],
                        "station_id": station_id,
                        "huc8": huc8,
                        "parameter_code": parameter,
                        "value": value,
                        "unit": output_unit,
                        "longitude": coordinates[0],
                        "latitude": coordinates[1],
                        "quality": (status or "") + "|" + (qualifiers or ""),
                    }
                )
    frame = pd.DataFrame(rows, columns=OBSERVATION_COLUMNS)
    frame["date"] = pd.to_datetime(frame["date"], utc=True).dt.tz_localize(None).dt.normalize()
    return frame.sort_values(["date", "station_id", "parameter_code"]).reset_index(drop=True)


def station_series(observations: pd.DataFrame, parameter_code: str = "00060") -> pd.DataFrame:
    if parameter_code not in PARAMETERS:
        raise ValueError("unsupported water parameter")
    subset = observations.loc[observations["parameter_code"] == parameter_code]
    if subset.empty:
        return pd.DataFrame(index=pd.DatetimeIndex([], name="date"))
    return subset.pivot_table(index="date", columns="station_id", values="value", aggfunc="mean")
