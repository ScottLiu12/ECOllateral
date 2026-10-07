import re
from datetime import date

import httpx
import numpy as np
import pandas as pd

DATA_URL = "https://www.ncei.noaa.gov/access/services/data/v1"
CLIMDIV_URL = "https://www.ncei.noaa.gov/pub/data/cirs/climdiv/"


def wet_bulb_from_dewpoint(dry: pd.Series, dew: pd.Series) -> tuple[pd.Series, pd.Series]:
    valid_dew = dew.where(dew <= dry)
    rh = 100 * np.exp(17.625 * valid_dew / (243.04 + valid_dew) - 17.625 * dry / (243.04 + dry))
    # Stull (2011), sea-level approximation. Reject cold/dry and out-of-domain inputs.
    valid = dry.between(-20, 50) & rh.between(5, 99) & ~((dry < 0) & (rh < 20))
    wet = (
        dry * np.arctan(0.151977 * np.sqrt(rh + 8.313659))
        + np.arctan(dry + rh)
        - np.arctan(rh - 1.676331)
        + 0.00391838 * rh**1.5 * np.arctan(0.023101 * rh)
        - 4.686035
    )
    wet = wet.where(valid).clip(upper=dry)
    # Saturation has an exact solution and lies just outside the approximation's range.
    wet = wet.where(~np.isclose(rh, 100, atol=1e-6), dry)
    return wet, rh


def fetch_daily_weather(client: httpx.Client, station: str, start: date, end: date) -> pd.DataFrame:
    if not re.fullmatch(r"[0-9]{11}", station):
        raise ValueError("GSOD station must be its 11-digit USAF/WBAN identifier")
    if end < start:
        raise ValueError("end must be on or after start")
    response = client.get(
        DATA_URL,
        params={
            "dataset": "global-summary-of-the-day",
            "stations": station,
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dataTypes": "TEMP,DEWP,PRCP",
            "format": "json",
            "units": "standard",
            "includeAttributes": "true",
        },
    )
    response.raise_for_status()
    raw = pd.DataFrame(response.json())
    if raw.empty:
        return pd.DataFrame(
            columns=[
                "date",
                "station_id",
                "dry_bulb_c",
                "dew_point_c",
                "wet_bulb_c",
                "relative_humidity_pct",
                "precipitation_mm",
            ]
        )
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(raw["DATE"]).dt.normalize(),
            "station_id": station,
        }
    )
    for source, output in (("TEMP", "dry_bulb_c"), ("DEWP", "dew_point_c")):
        values = pd.to_numeric(raw[source], errors="coerce")
        frame[output] = (values.where(values < 9999) - 32) * 5 / 9
    precipitation = pd.to_numeric(raw["PRCP"], errors="coerce")
    frame["precipitation_mm"] = precipitation.where(precipitation.between(0, 99.98)) * 25.4
    frame["wet_bulb_c"], frame["relative_humidity_pct"] = wet_bulb_from_dewpoint(
        frame["dry_bulb_c"], frame["dew_point_c"]
    )
    frame["wet_bulb_method"] = "Stull_2011_sea_level_approximation"
    for field in ("TEMP_ATTRIBUTES", "DEWP_ATTRIBUTES", "PRCP_ATTRIBUTES"):
        if field in raw:
            frame[field.lower()] = raw[field]
    return frame.sort_values("date").reset_index(drop=True)


def fetch_pdsi(client: httpx.Client, climate_division: str, start: date, end: date) -> pd.DataFrame:
    if not re.fullmatch(r"[0-9]{4}", climate_division):
        raise ValueError("climate_division must be four digits (state + division)")
    if end < start:
        raise ValueError("end must be on or after start")
    listing = client.get(CLIMDIV_URL)
    listing.raise_for_status()
    filenames = re.findall(r"climdiv-pdsidv-v1\.0\.0-[0-9]{8}", listing.text)
    if not filenames:
        raise ValueError("NOAA directory did not list a divisional PDSI file")
    filename = max(filenames)
    response = client.get(CLIMDIV_URL + filename)
    response.raise_for_status()
    rows = []
    for line in response.text.splitlines():
        fields = line.split()
        if not fields or len(fields[0]) != 10 or not fields[0].startswith(climate_division + "05"):
            continue
        year = int(fields[0][6:10])
        if len(fields) != 13:
            raise ValueError("unexpected nClimDiv monthly record format")
        for month, raw in enumerate(fields[1:], 1):
            timestamp = pd.Timestamp(year=year, month=month, day=1)
            if start.replace(day=1) <= timestamp.date() <= end.replace(day=1):
                value = float(raw)
                rows.append(
                    {
                        "date": timestamp,
                        "pdsi": value if value > -99 else np.nan,
                        "climate_division": climate_division,
                        "source": filename,
                    }
                )
    return pd.DataFrame(rows, columns=["date", "pdsi", "climate_division", "source"])
