from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

MISSING_RATES = (0.10, 0.25, 0.40)


def drought_mask(
    series: pd.Series, drought: pd.Series, rate: float, rng: np.random.Generator
) -> pd.Series:
    if not 0 < rate < 1:
        raise ValueError("missingness rate must be between 0 and 1")
    eligible = series.notna() & drought.reindex(series.index, fill_value=False).fillna(False)
    positions = np.flatnonzero(eligible.to_numpy())
    if len(positions) == 0:
        raise ValueError("no observed drought records available to mask")
    count = max(1, round(len(positions) * rate))
    mask = pd.Series(False, index=series.index)
    mask.iloc[rng.choice(positions, size=count, replace=False)] = True
    return mask


def linear_fill(series: pd.Series) -> pd.Series:
    if not isinstance(series.index, pd.DatetimeIndex) or not series.index.is_monotonic_increasing:
        raise ValueError("linear filling requires a sorted DatetimeIndex")
    # Historical reconstruction only: future observations are used inside gaps.
    return series.interpolate(method="time", limit_area="inside").ffill().bfill()


def spatial_fill(stations: pd.DataFrame, target: str, coordinates: pd.DataFrame) -> pd.Series:
    if target not in stations:
        raise ValueError("target station is not in the series matrix")
    if not stations.columns.isin(coordinates.index).all():
        raise ValueError("all stations need latitude and longitude")
    coords = coordinates.loc[stations.columns, ["latitude", "longitude"]].astype(float)
    if not np.isfinite(coords.to_numpy()).all():
        raise ValueError("station coordinates must be finite")
    if not coords.latitude.between(-90, 90).all() or not coords.longitude.between(-180, 180).all():
        raise ValueError("invalid station coordinates")
    lat, lon = np.radians(coords.latitude), np.radians(coords.longitude)
    distances = np.sin((lat - lat[target]) / 2) ** 2 + (
        np.cos(lat) * np.cos(lat[target]) * np.sin((lon - lon[target]) / 2) ** 2
    )
    result = stations[target].copy()
    for donor in distances.drop(target).sort_values().index:
        result = result.fillna(stations[donor])
    return result


@dataclass
class SensitivityResult:
    summary: pd.DataFrame
    bands: pd.DataFrame


def analyze_missingness(
    stations: pd.DataFrame,
    target: str,
    coordinates: pd.DataFrame,
    features: pd.DataFrame,
    predict: Callable[[pd.DataFrame], np.ndarray],
    *,
    drought: pd.Series | None = None,
    rates: tuple[float, ...] = MISSING_RATES,
    repeats: int = 50,
    tolerance_mgd: float = 0.05,
    seed: int = 42,
) -> SensitivityResult:
    if repeats < 20 or tolerance_mgd <= 0 or not np.isfinite(tolerance_mgd):
        raise ValueError("use at least 20 repeats and a finite positive tolerance")
    if not stations.index.equals(features.index) or not stations.index.is_unique:
        raise ValueError("station records and features need the same unique date index")
    if (
        not isinstance(stations.index, pd.DatetimeIndex)
        or not stations.index.is_monotonic_increasing
    ):
        raise ValueError("station records need a sorted DatetimeIndex")
    if target not in stations or stations[target].isna().any():
        raise ValueError("the reference target series must be complete before synthetic masking")
    drought = (features["pdsi"] <= -2) if drought is None else drought.reindex(stations.index)
    drought = drought.fillna(False).astype(bool)
    if not drought.any():
        raise ValueError("no drought records to evaluate")
    baseline_features = features.copy()
    baseline_features["historical_streamflow_mgd"] = stations[target]
    baseline = np.asarray(predict(baseline_features), dtype=float)
    if baseline.shape != (len(features),) or not np.isfinite(baseline).all():
        raise ValueError("predict must return one finite value per record")
    rng = np.random.default_rng(seed)
    summaries, bands = [], []
    for rate in rates:
        draws = {"spatial_nearest": [], "linear_time": []}
        missing_counts = []
        for _ in range(repeats):
            mask = drought_mask(stations[target], drought, rate, rng)
            missing_counts.append(int(mask.sum()))
            masked = stations.copy()
            masked.loc[mask, target] = np.nan
            filled = {
                "spatial_nearest": spatial_fill(masked, target, coordinates),
                "linear_time": linear_fill(masked[target]),
            }
            for strategy, values in filled.items():
                if values.isna().any():
                    raise ValueError(f"{strategy}: unresolved gaps; supply adjacent stations")
                trial = baseline_features.copy()
                trial["historical_streamflow_mgd"] = values
                predicted = np.asarray(predict(trial), dtype=float)
                if predicted.shape != baseline.shape or not np.isfinite(predicted).all():
                    raise ValueError("predict returned invalid trial forecasts")
                draws[strategy].append(predicted)
        for strategy, values in draws.items():
            predictions = np.stack(values)
            low, high = np.quantile(predictions, [0.05, 0.95], axis=0)
            deviations = predictions[:, drought.to_numpy()] - baseline[drought.to_numpy()]
            band_ok = (low >= baseline - tolerance_mgd) & (high <= baseline + tolerance_mgd)
            coverage = float(np.mean(np.abs(deviations) <= tolerance_mgd))
            summaries.append(
                {
                    "missing_rate": rate,
                    "strategy": strategy,
                    "repeats": repeats,
                    "drought_records": int(drought.sum()),
                    "dropped_per_repeat": missing_counts[0],
                    "prediction_variance_mgd2": float(
                        np.mean(np.var(predictions[:, drought.to_numpy()], axis=0, ddof=1))
                    ),
                    "tolerance_coverage": coverage,
                    "drought_band_within_tolerance_fraction": float(
                        band_ok[drought.to_numpy()].mean()
                    ),
                    "stable": bool(coverage >= 0.9 and band_ok[drought.to_numpy()].all()),
                }
            )
            bands.append(
                pd.DataFrame(
                    {
                        "date": features.index,
                        "missing_rate": rate,
                        "strategy": strategy,
                        "baseline_mgd": baseline,
                        "band90_low_mgd": low,
                        "band90_high_mgd": high,
                        "prediction_std_mgd": predictions.std(axis=0, ddof=1),
                        "drought": drought.to_numpy(),
                    }
                )
            )
    return SensitivityResult(pd.DataFrame(summaries), pd.concat(bands, ignore_index=True))
