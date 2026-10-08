from pathlib import Path

import numpy as np
import pandas as pd

from src.grounding.chunking import PermitSection, chunk_section
from src.grounding.store import PermitStore
from src.models.feature_pipeline import seasonal_factor
from src.models.regression import train_model
from src.rules.thermodynamic import CoolingType


def training_data(rows_per_type: int = 1600, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    frames = []
    for cooling in CoolingType:
        dates = pd.Timestamp("2018-01-01") + pd.to_timedelta(
            rng.integers(0, 6 * 365, rows_per_type), unit="D"
        )
        months = pd.Series(dates.month)
        season = seasonal_factor(months).to_numpy()
        dry = 14 + 15 * season + rng.normal(0, 2, rows_per_type)
        flow = rng.uniform(15, 250, rows_per_type)
        pdsi = rng.uniform(-5, 3, rows_per_type)
        mw = rng.uniform(5, 80, rows_per_type)
        # An invented response surface for exercising training; no measured facility labels.
        target = (
            mw
            * 0.0045
            * (0.8 + dry / 100)
            * (1 + np.maximum(-pdsi, 0) / 100)
            * (1 + 0.08 * np.exp(-flow / 100))
        )
        if cooling == CoolingType.DIRECT_EVAPORATIVE:
            target *= 0.75
        if cooling == CoolingType.AIR_COOLED:
            target = np.zeros(rows_per_type)
        else:
            target = np.maximum(0, target + rng.normal(0, 0.003, rows_per_type))
        frames.append(
            pd.DataFrame(
                {
                    "date": dates,
                    "facility_mw": mw,
                    "dry_bulb_c": dry,
                    "wet_bulb_c": dry - rng.uniform(4, 12, rows_per_type),
                    "historical_streamflow_mgd": flow,
                    "pdsi": pdsi,
                    "cooling_type": cooling.value,
                    "consumption_mgd": target,
                }
            )
        )
    return pd.concat(frames, ignore_index=True).sort_values("date").reset_index(drop=True)


def hydrology_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    dates = pd.date_range("2023-01-01", periods=365)
    time = np.arange(len(dates))
    drought = (time >= 150) & (time <= 270)
    flow = 85 + 10 * np.sin(time / 14) - 35 * drought
    stations = pd.DataFrame(
        {
            "target": flow,
            "adjacent_a": flow + 0.8 * np.sin(time / 7),
            "adjacent_b": flow + 1.2 * np.cos(time / 9),
        },
        index=dates,
    )
    coordinates = pd.DataFrame(
        {
            "latitude": [38.9, 38.92, 39.0],
            "longitude": [-77.1, -77.12, -77.2],
        },
        index=stations.columns,
    )
    season = seasonal_factor(pd.Series(dates.month, index=dates))
    features = pd.DataFrame(
        {
            "facility_mw": 40.0,
            "dry_bulb_c": 14 + 15 * season,
            "wet_bulb_c": 6 + 15 * season,
            "historical_streamflow_mgd": flow,
            "pdsi": np.where(drought, -3.0, 0.0),
            "month": dates.month,
        },
        index=dates,
    )
    return stations, coordinates, features


def create_demo(directory: Path) -> None:
    import json

    directory.mkdir(parents=True, exist_ok=True)
    data = training_data()
    data.to_csv(directory / "training.csv", index=False)
    model = train_model(data, data_kind="synthetic")
    model.save(directory / "model.joblib")
    (directory / "benchmark.json").write_text(
        json.dumps(
            {"data_kind": "synthetic", "benchmark": model.benchmark}, indent=2, allow_nan=False
        )
        + "\n",
        encoding="utf-8",
    )
    stations, coordinates, features = hydrology_data()
    stations.rename_axis("date").to_csv(directory / "stations.csv")
    coordinates.rename_axis("station_id").to_csv(directory / "coordinates.csv")
    features.rename_axis("date").to_csv(directory / "daily_features.csv")
    environment = (
        features.groupby("month")[["dry_bulb_c", "wet_bulb_c", "historical_streamflow_mgd", "pdsi"]]
        .median()
        .reset_index()
    )
    environment["huc8"] = "02070010"
    environment["latitude"], environment["longitude"] = 38.9, -77.1
    environment["data_kind"] = "synthetic"
    environment["source_period_start"], environment["source_period_end"] = (
        "2023-01-01",
        "2023-12-31",
    )
    environment.to_csv(directory / "environment.csv", index=False)
    section = PermitSection(
        document_id="demo-permit",
        title="Fictional municipal cooling-water permit",
        section="IV.B",
        text="Example only: cooling-water withdrawals require monthly "
        "reporting to the municipal utility. This text is not an actual permit or water cap.",
        source_url="https://example.org/ecollateral-demo-permit",
        huc8=("02070010",),
        is_example=True,
    )
    PermitStore(chunk_section(section)).save(directory / "permits")
