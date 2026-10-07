from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

from src.models.evaluation import Metrics, evaluate
from src.models.feature_pipeline import FEATURE_COLUMNS, build_features
from src.rules.thermodynamic import CoolingType, ThermalAssumptions, WaterBounds, water_bounds


@dataclass
class CoolingModel:
    estimator: Pipeline
    name: str
    metrics: Metrics
    residual90_mgd: float
    feature_ranges: dict[str, tuple[float, float]]


@dataclass(frozen=True)
class Prediction:
    raw_mgd: float
    predicted_mgd: float
    bounds: WaterBounds
    interval90_min_mgd: float
    interval90_max_mgd: float
    heldout_r2: float | None
    warnings: tuple[str, ...]


@dataclass
class ForecastModel:
    models: dict[str, CoolingModel]
    benchmark: dict
    data_kind: str
    assumptions: ThermalAssumptions
    artifact_version: int = 1

    def predict(self, records: pd.DataFrame, cooling_type: CoolingType | str) -> list[Prediction]:
        cooling_type = CoolingType(cooling_type)
        if cooling_type.value not in self.models:
            raise ValueError(f"no trained model for {cooling_type.value}")
        features = build_features(records)
        model = self.models[cooling_type.value]
        raw = np.asarray(model.estimator.predict(features), dtype=float)
        if not np.isfinite(raw).all():
            raise ValueError("model produced a non-finite forecast")
        results = []
        for (_, row), value in zip(features.iterrows(), raw, strict=True):
            bounds = water_bounds(
                row.facility_mw, cooling_type, row.dry_bulb_c, row.wet_bulb_c, self.assumptions
            )
            clipped = float(np.clip(value, bounds.min_mgd, bounds.max_mgd))
            warnings = list(bounds.warnings)
            if clipped != value:
                warnings.append("constraint_violation")
            if row.isna().any():
                warnings.append("missing_environmental_features_imputed")
            if any(
                pd.notna(row[name]) and not low <= row[name] <= high
                for name, (low, high) in model.feature_ranges.items()
            ):
                warnings.append("outside_training_feature_range")
            if self.data_kind == "synthetic":
                warnings.append("synthetic_model_not_validated_for_real_facilities")
            results.append(
                Prediction(
                    raw_mgd=float(value),
                    predicted_mgd=clipped,
                    bounds=bounds,
                    interval90_min_mgd=max(bounds.min_mgd, clipped - model.residual90_mgd),
                    interval90_max_mgd=min(bounds.max_mgd, clipped + model.residual90_mgd),
                    heldout_r2=model.metrics.r2,
                    warnings=tuple(warnings),
                )
            )
        return results

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: Path) -> "ForecastModel":
        # Pickle/joblib artifacts must come from a trusted local training run.
        model = joblib.load(path)
        if not isinstance(model, cls) or model.artifact_version != 1:
            raise ValueError("unsupported forecast model artifact")
        return model


def _clip_predictions(
    values: np.ndarray, features: pd.DataFrame, cooling: str, assumptions: ThermalAssumptions
) -> np.ndarray:
    bounds = [
        water_bounds(row.facility_mw, cooling, row.dry_bulb_c, row.wet_bulb_c, assumptions)
        for row in features.itertuples(index=False)
    ]
    return np.clip(values, [bound.min_mgd for bound in bounds], [bound.max_mgd for bound in bounds])


def train_model(
    records: pd.DataFrame,
    *,
    data_kind: str = "observed",
    seed: int = 42,
    assumptions: ThermalAssumptions | None = None,
) -> ForecastModel:
    if data_kind not in ("observed", "synthetic"):
        raise ValueError("data_kind must be observed or synthetic")
    assumptions = assumptions or ThermalAssumptions()
    required = {"date", "cooling_type", "consumption_mgd"}
    if not required.issubset(records.columns):
        raise ValueError(f"training requires {', '.join(sorted(required))}")
    frame = records.copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="raise", utc=True).dt.normalize()
    if frame["date"].isna().any() or frame["cooling_type"].isna().any():
        raise ValueError("training dates and cooling types cannot be missing")
    frame["month"] = frame["date"].dt.month
    frame["consumption_mgd"] = pd.to_numeric(frame["consumption_mgd"], errors="raise")
    if not np.isfinite(frame["consumption_mgd"]).all() or (frame["consumption_mgd"] < 0).any():
        raise ValueError("training targets must be finite, nonnegative MGD")
    models, benchmark = {}, {}
    for cooling, group in frame.groupby("cooling_type", sort=True):
        cooling = CoolingType(cooling).value
        group = group.sort_values("date")
        dates = group["date"].drop_duplicates().to_numpy()
        if len(dates) < 30:
            raise ValueError(
                f"{cooling}: at least 30 distinct dates required for temporal holdouts"
            )
        train_end, calibration_end = dates[int(len(dates) * 0.6)], dates[int(len(dates) * 0.8)]
        subsets = [
            group[group.date < train_end],
            group[(group.date >= train_end) & (group.date < calibration_end)],
            group[group.date >= calibration_end],
        ]
        x_train, x_cal, x_test = [build_features(subset) for subset in subsets]
        y_train, y_cal, y_test = [subset["consumption_mgd"].to_numpy() for subset in subsets]
        if x_train.isna().all().any():
            raise ValueError(f"{cooling}: a training feature has no observed values")
        candidates = {
            "random_forest": RandomForestRegressor(
                n_estimators=180,
                min_samples_leaf=2,
                n_jobs=1,
                random_state=seed,
            ),
            "xgboost": XGBRegressor(
                n_estimators=240,
                max_depth=4,
                learning_rate=0.06,
                subsample=0.9,
                colsample_bytree=1,
                objective="reg:squarederror",
                n_jobs=1,
                random_state=seed,
            ),
        }
        fitted, calibration_scores, results = {}, {}, {}
        for name, estimator in candidates.items():
            pipeline = Pipeline(
                [
                    ("impute", SimpleImputer(strategy="median", add_indicator=True)),
                    ("regress", estimator),
                ]
            )
            pipeline.fit(x_train, y_train)
            calibration = pipeline.predict(x_cal)
            test = pipeline.predict(x_test)
            fitted[name] = pipeline
            calibration_scores[name] = evaluate(y_cal, calibration)
            results[name] = {
                "calibration": calibration_scores[name].to_dict(),
                "test_raw": evaluate(y_test, test).to_dict(),
                "test_bounded": evaluate(
                    y_test, _clip_predictions(test, x_test, cooling, assumptions)
                ).to_dict(),
            }
        selected = min(calibration_scores, key=lambda name: calibration_scores[name].rmse_mgd)
        pipeline = fitted[selected]
        cal_pred = _clip_predictions(pipeline.predict(x_cal), x_cal, cooling, assumptions)
        residuals = np.abs(y_cal - cal_pred)
        # Split conformal finite-sample quantile; calibration points never enter fitting.
        level = min(1, np.ceil((len(residuals) + 1) * 0.9) / len(residuals))
        radius = float(np.quantile(residuals, level, method="higher"))
        test_pred = _clip_predictions(pipeline.predict(x_test), x_test, cooling, assumptions)
        coverage = float(np.mean(np.abs(y_test - test_pred) <= radius))
        models[cooling] = CoolingModel(
            estimator=pipeline,
            name=selected,
            metrics=evaluate(y_test, test_pred),
            residual90_mgd=radius,
            feature_ranges={
                name: (float(x_train[name].min()), float(x_train[name].max()))
                for name in FEATURE_COLUMNS
            },
        )
        benchmark[cooling] = {
            "selected": selected,
            "candidates": results,
            "interval90_radius_mgd": radius,
            "test_interval90_coverage": coverage,
            "split": {
                "method": "chronological_60_20_20",
                "train_rows": len(x_train),
                "calibration_rows": len(x_cal),
                "test_rows": len(x_test),
                "train_end_exclusive": str(train_end),
                "calibration_end_exclusive": str(calibration_end),
            },
        }
    if not models:
        raise ValueError("training dataset is empty")
    return ForecastModel(models, benchmark, data_kind, assumptions)
