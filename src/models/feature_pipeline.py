import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "facility_mw",
    "dry_bulb_c",
    "wet_bulb_c",
    "historical_streamflow_mgd",
    "pdsi",
    "seasonal_factor",
]
OPTIONAL_FEATURES = ["historical_streamflow_mgd", "pdsi"]


def seasonal_factor(months: pd.Series) -> pd.Series:
    months = pd.to_numeric(months, errors="raise")
    if months.isna().any() or not months.between(1, 12).all() or (months % 1 != 0).any():
        raise ValueError("month must contain integers from 1 to 12")
    return 0.5 * (1 + np.cos(2 * np.pi * (months - 7) / 12))


def build_features(records: pd.DataFrame) -> pd.DataFrame:
    frame = records.copy()
    if "seasonal_factor" not in frame and "month" in frame:
        frame["seasonal_factor"] = seasonal_factor(frame["month"])
    missing = set(FEATURE_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"missing feature columns: {', '.join(sorted(missing))}")
    frame = frame[FEATURE_COLUMNS].apply(pd.to_numeric, errors="raise").astype(float)
    if np.isinf(frame.to_numpy()).any():
        raise ValueError("features cannot contain infinite values")
    required = [column for column in FEATURE_COLUMNS if column not in OPTIONAL_FEATURES]
    if frame[required].isna().any().any():
        raise ValueError("capacity, temperatures, and season cannot be missing")
    if (frame["facility_mw"] < 0).any():
        raise ValueError("facility_mw cannot be negative")
    if not frame["dry_bulb_c"].between(-20, 50).all():
        raise ValueError("dry_bulb_c must be between -20 and 50 C")
    if (frame["wet_bulb_c"] < -30).any() or (
        frame["wet_bulb_c"] > frame["dry_bulb_c"]
    ).any():
        raise ValueError("invalid wet-bulb temperature")
    if (frame["historical_streamflow_mgd"].dropna() < 0).any():
        raise ValueError("streamflow cannot be negative")
    if not frame["pdsi"].dropna().between(-15, 15).all():
        raise ValueError("pdsi must be between -15 and 15")
    if not frame["seasonal_factor"].between(0, 1).all():
        raise ValueError("seasonal_factor must be between 0 and 1")
    return frame
