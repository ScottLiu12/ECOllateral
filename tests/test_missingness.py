import numpy as np
import pandas as pd
import pytest

from src.demo import hydrology_data
from src.models.missingness import (
    MISSING_RATES,
    analyze_missingness,
    drought_mask,
    linear_fill,
    spatial_fill,
)


@pytest.mark.parametrize("rate", MISSING_RATES)
def test_mask_only_drops_requested_fraction_of_observed_drought_records(rate):
    index = pd.date_range("2024-01-01", periods=100)
    series = pd.Series(np.arange(100, dtype=float), index=index)
    series.iloc[50:60] = np.nan
    drought = pd.Series(False, index=index)
    drought.iloc[20:80] = True
    mask = drought_mask(series, drought, rate, np.random.default_rng(42))
    assert mask.sum() == round(50 * rate)
    assert not mask[~drought].any()
    assert not mask[series.isna()].any()


def test_linear_interpolation_uses_elapsed_time_and_fills_edges():
    series = pd.Series(
        [np.nan, 1.0, np.nan, 11.0, np.nan],
        index=pd.to_datetime(
            [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-12",
                "2024-01-13",
            ]
        ),
    )
    np.testing.assert_allclose(linear_fill(series), [1, 1, 2, 11, 11])


def test_spatial_uses_nearest_available_donor_and_preserves_observed_values():
    stations, coords, _ = hydrology_data()
    stations.iloc[0, 0] = np.nan
    stations.iloc[0, 1] = np.nan
    stations.iloc[1, 0] = np.nan
    result = spatial_fill(stations, "target", coords)
    assert result.iloc[0] == stations.adjacent_b.iloc[0]
    assert result.iloc[1] == stations.adjacent_a.iloc[1]
    np.testing.assert_allclose(result.iloc[2:], stations.target.iloc[2:])


def test_real_regressor_sensitivity_reports_all_rates(fitted_model):
    stations, coords, features = hydrology_data()

    def predict(frame):
        return np.array(
            [result.predicted_mgd for result in fitted_model.predict(frame, "cooling_tower")]
        )

    result = analyze_missingness(stations, "target", coords, features, predict, repeats=20)
    assert len(result.summary) == 6
    assert result.summary.prediction_variance_mgd2.ge(0).all()
    assert result.summary.tolerance_coverage.between(0, 1).all()
    assert (result.bands.band90_high_mgd >= result.bands.band90_low_mgd).all()


def test_analysis_detects_unstable_spatial_reconstruction():
    stations, coords, features = hydrology_data()
    stations["adjacent_a"] += 100
    stations["adjacent_b"] += 100
    result = analyze_missingness(
        stations,
        "target",
        coords,
        features,
        lambda frame: frame.historical_streamflow_mgd.to_numpy() * 0.01,
        repeats=20,
        rates=(0.4,),
    )
    spatial = result.summary[result.summary.strategy == "spatial_nearest"].iloc[0]
    assert not spatial.stable
    assert spatial.tolerance_coverage < 0.9


@pytest.mark.parametrize("rate", MISSING_RATES)
def test_groundwater_depth_gaps_use_the_same_masks_without_unit_conversion(rate):
    stations, coords, features = hydrology_data()
    depths_m = 20 + stations / 100
    mask = drought_mask(depths_m.target, features.pdsi <= -2, rate, np.random.default_rng(5))
    masked = depths_m.copy()
    masked.loc[mask, "target"] = np.nan
    for filled in (spatial_fill(masked, "target", coords), linear_fill(masked.target)):
        assert filled.notna().all()
        assert np.abs(filled[mask] - depths_m.target[mask]).max() < 0.4


def test_missing_reference_and_donors_are_reported():
    stations, coords, features = hydrology_data()
    stations.iloc[0, 0] = np.nan
    with pytest.raises(ValueError, match="reference"):
        analyze_missingness(
            stations, "target", coords, features, lambda frame: np.zeros(len(frame))
        )
