import math

import pytest

from src.rules.thermodynamic import (
    LITERS_PER_MILLION_GALLONS,
    CoolingType,
    ThermalAssumptions,
    water_bounds,
)


def test_evaporative_bound_has_correct_energy_and_volume_units():
    bound = water_bounds(10, "cooling_tower", 30, 20)
    assert bound.thermal_load_kwh_day == 288_000
    expected = 288_000 * 3600 / (2501 - 2.361 * 20) / LITERS_PER_MILLION_GALLONS
    assert bound.min_mgd == 0
    assert bound.max_mgd == pytest.approx(expected)
    assert bound.max_site_wue_l_per_it_kwh == pytest.approx(bound.max_liters_per_thermal_kwh * 1.2)


@pytest.mark.parametrize("cooling", list(CoolingType))
def test_zero_capacity_consumes_no_water(cooling):
    assert water_bounds(0, cooling, 30, 20).max_mgd == 0


def test_dry_cooling_and_scaling():
    assert water_bounds(100, "air_cooled", 35, 25).max_mgd == 0
    low = water_bounds(10, "direct_evaporative", 35, 20)
    high = water_bounds(100, "direct_evaporative", 35, 20)
    assert high.max_mgd == pytest.approx(10 * low.max_mgd)
    half = water_bounds(100, "direct_evaporative", 35, 20, ThermalAssumptions(utilization=0.5))
    assert half.max_mgd == pytest.approx(high.max_mgd / 2)


@pytest.mark.parametrize(
    "mw,dry,wet", [(-1, 30, 20), (math.nan, 30, 20), (10, 20, 21), (10, 51, 20)]
)
def test_invalid_conditions_rejected(mw, dry, wet):
    with pytest.raises(ValueError):
        water_bounds(mw, "cooling_tower", dry, wet)


def test_saturated_air_flags_design_review():
    assert water_bounds(50, "direct_evaporative", 30, 30).warnings


@pytest.mark.parametrize("kwargs", [{"pue": 0.9}, {"utilization": 2}, {"pue": math.inf}])
def test_invalid_assumptions(kwargs):
    with pytest.raises(ValueError):
        ThermalAssumptions(**kwargs)
