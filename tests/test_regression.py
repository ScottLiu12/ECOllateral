from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from src.models.evaluation import evaluate
from src.models.feature_pipeline import FEATURE_COLUMNS, build_features
from src.models.regression import ForecastModel, train_model


def facility():
    return pd.DataFrame(
        [
            {
                "facility_mw": 40.0,
                "dry_bulb_c": 30.0,
                "wet_bulb_c": 20.0,
                "historical_streamflow_mgd": 70.0,
                "pdsi": -3.0,
                "month": 7,
            }
        ]
    )


def test_benchmarks_on_known_synthetic_response(fitted_model):
    for cooling in ("cooling_tower", "direct_evaporative"):
        report = fitted_model.benchmark[cooling]
        assert set(report["candidates"]) == {"random_forest", "xgboost"}
        assert report["candidates"][report["selected"]]["test_bounded"]["target_met"]
        assert report["split"]["train_end_exclusive"] < report["split"]["calibration_end_exclusive"]
    assert fitted_model.models["air_cooled"].metrics.r2 is None


@pytest.mark.parametrize("raw", [-1.0, 1_000_000.0])
def test_clips_impossible_predictions_and_keeps_raw(fitted_model, monkeypatch, raw):
    model = fitted_model.models["cooling_tower"]
    monkeypatch.setattr(
        model, "estimator", SimpleNamespace(predict=lambda frame: np.full(len(frame), raw))
    )
    prediction = fitted_model.predict(facility(), "cooling_tower")[0]
    assert prediction.raw_mgd == raw
    assert "constraint_violation" in prediction.warnings
    assert prediction.predicted_mgd == (
        prediction.bounds.min_mgd if raw < 0 else prediction.bounds.max_mgd
    )
    assert prediction.bounds.min_mgd <= prediction.interval90_min_mgd
    assert prediction.interval90_max_mgd <= prediction.bounds.max_mgd


def test_artifact_reload_and_missing_features(fitted_model, tmp_path):
    path = tmp_path / "model.joblib"
    fitted_model.save(path)
    restored = ForecastModel.load(path)
    features = facility()
    features["pdsi"] = np.nan
    prediction = restored.predict(features, "cooling_tower")[0]
    assert "missing_environmental_features_imputed" in prediction.warnings
    assert prediction.predicted_mgd >= 0
    assert prediction.heldout_r2 > 0.8


def test_imputer_fits_training_period_only(fitted_model, training_records):
    group = training_records[training_records.cooling_type == "cooling_tower"].copy()
    dates = np.sort(group.date.unique())
    train_end = dates[int(len(dates) * 0.6)]
    train = group[group.date < train_end].copy()
    train["month"] = train.date.dt.month
    expected = build_features(train).median().to_numpy()
    fitted = fitted_model.models["cooling_tower"].estimator.named_steps["impute"].statistics_
    np.testing.assert_allclose(fitted, expected)
    assert list(build_features(facility()).columns) == FEATURE_COLUMNS


def test_invalid_targets_and_features(training_records):
    data = training_records.copy()
    data.loc[0, "consumption_mgd"] = -1
    with pytest.raises(ValueError, match="nonnegative"):
        train_model(data)
    features = facility()
    features["wet_bulb_c"] = 40
    with pytest.raises(ValueError, match="wet-bulb"):
        build_features(features)
    assert evaluate(np.zeros(3), np.zeros(3)).r2 is None
