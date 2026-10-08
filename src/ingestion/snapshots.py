from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.geography import distance_km


def monthly_snapshots(
    observations: pd.DataFrame,
    weather: pd.DataFrame,
    pdsi: pd.DataFrame,
    huc8: str,
    flow_station: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    flow = observations[
        (observations.station_id == flow_station) & (observations.parameter_code == "00060")
    ]
    if flow.empty or flow.value.isna().all() or weather.empty:
        raise ValueError("the selected station needs streamflow and NOAA weather observations")
    flow_series = flow.groupby("date").value.mean().rename("historical_streamflow_mgd")
    daily = weather.set_index("date").join(flow_series)
    drought = pdsi.set_index("date")["pdsi"] if not pdsi.empty else pd.Series(dtype=float)
    daily["pdsi"] = daily.index.to_period("M").to_timestamp().map(drought)
    daily["month"] = daily.index.month
    columns = ["dry_bulb_c", "wet_bulb_c", "historical_streamflow_mgd", "pdsi"]
    monthly = daily.groupby("month")[columns].median().reset_index()
    monthly["huc8"] = huc8
    monthly["latitude"] = flow.iloc[0].latitude
    monthly["longitude"] = flow.iloc[0].longitude
    monthly["data_kind"] = "observed"
    monthly["source_period_start"] = daily.index.min().date().isoformat()
    monthly["source_period_end"] = daily.index.max().date().isoformat()
    monthly["flow_station_id"] = flow_station
    monthly["noaa_station_id"] = weather.iloc[0].station_id
    monthly["climate_division"] = pdsi.iloc[0].climate_division if not pdsi.empty else ""
    monthly["weather_record_count"] = daily.groupby("month")["dry_bulb_c"].count().to_numpy()
    monthly["streamflow_record_count"] = (
        daily.groupby("month")["historical_streamflow_mgd"].count().to_numpy()
    )
    # Missing months are omitted, not replaced with a different month's conditions.
    monthly = monthly.dropna(subset=["dry_bulb_c", "wet_bulb_c", "latitude", "longitude"])
    return daily.reset_index(), monthly.reset_index(drop=True)


@dataclass(frozen=True)
class EnvironmentSnapshot:
    values: dict
    warnings: tuple[str, ...]


class EnvironmentData:
    def __init__(self, records: pd.DataFrame) -> None:
        self.records = records.copy()
        required = {
            "huc8",
            "month",
            "latitude",
            "longitude",
            "dry_bulb_c",
            "wet_bulb_c",
            "historical_streamflow_mgd",
            "pdsi",
            "data_kind",
            "source_period_start",
            "source_period_end",
        }
        if not required.issubset(records.columns) or records.empty:
            raise ValueError("environment snapshots are missing required columns or rows")
        if not records.huc8.astype(str).str.fullmatch(r"[0-9]{8}").all():
            raise ValueError("environment snapshots need eight-digit HUC IDs")
        if records.duplicated(["huc8", "month"]).any():
            raise ValueError("environment snapshots must have one row per HUC/month")
        if not records.data_kind.isin(["observed", "synthetic"]).all():
            raise ValueError("environment data_kind must be observed or synthetic")
        if not records.month.between(1, 12).all() or (records.month % 1 != 0).any():
            raise ValueError("environment months must be integers from 1 to 12")
        if not np.isfinite(records[["latitude", "longitude"]].to_numpy(dtype=float)).all():
            raise ValueError("snapshot coordinates must be finite")
        if (
            not records.latitude.between(-90, 90).all()
            or not records.longitude.between(-180, 180).all()
        ):
            raise ValueError("invalid snapshot coordinates")

    @classmethod
    def load(cls, path: Path) -> "EnvironmentData":
        return cls(pd.read_csv(path, dtype={"huc8": str}))

    def resolve(
        self, month: int, huc8: str | None, latitude: float | None, longitude: float | None
    ) -> EnvironmentSnapshot:
        candidates = self.records[self.records.month == month]
        if huc8:
            candidates = candidates[candidates.huc8 == huc8]
        if candidates.empty:
            raise ValueError("no environmental snapshot for this location and seasonal month")
        warnings = ["historical_monthly_conditions_not_a_weather_forecast"]
        if latitude is not None and longitude is not None:
            distances = candidates.apply(
                lambda row: distance_km(latitude, longitude, row.latitude, row.longitude), axis=1
            )
            if distances.min() > 50:
                raise ValueError("no representative environmental station within 50 km")
            row = candidates.loc[distances.idxmin()]
            if huc8 is None:
                warnings.append("coordinates_resolved_to_nearest_station_huc")
        elif huc8:
            row = candidates.iloc[0]
        else:
            raise ValueError("provide huc8 or both coordinates")
        return EnvironmentSnapshot(row.to_dict(), tuple(warnings))
