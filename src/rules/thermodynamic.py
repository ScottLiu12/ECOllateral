from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

LITERS_PER_MILLION_GALLONS = 3_785_411.784


class CoolingType(StrEnum):
    DIRECT_EVAPORATIVE = "direct_evaporative"
    AIR_COOLED = "air_cooled"
    COOLING_TOWER = "cooling_tower"


@dataclass(frozen=True)
class ThermalAssumptions:
    # Capacity is IT power. Treat all site electrical energy as heat to be rejected.
    pue: float = 1.2
    utilization: float = 1.0
    evaporative_fraction_max: float = 1.0

    def __post_init__(self) -> None:
        if not isfinite(self.pue) or not 1 <= self.pue <= 3:
            raise ValueError("pue must be finite and between 1 and 3")
        for name in ("utilization", "evaporative_fraction_max"):
            value = getattr(self, name)
            if not isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be finite and between 0 and 1")


@dataclass(frozen=True)
class WaterBounds:
    min_mgd: float
    max_mgd: float
    thermal_load_kwh_day: float
    max_liters_per_thermal_kwh: float
    max_site_wue_l_per_it_kwh: float
    assumptions: ThermalAssumptions
    warnings: tuple[str, ...] = ()


def water_bounds(
    facility_mw: float,
    cooling_type: CoolingType | str,
    dry_bulb_c: float,
    wet_bulb_c: float,
    assumptions: ThermalAssumptions | None = None,
) -> WaterBounds:
    assumptions = assumptions or ThermalAssumptions()
    cooling_type = CoolingType(cooling_type)
    if not isfinite(facility_mw) or facility_mw < 0:
        raise ValueError("facility_mw must be finite and nonnegative")
    if not isfinite(dry_bulb_c) or not -20 <= dry_bulb_c <= 50:
        raise ValueError("dry_bulb_c must be between -20 and 50 C")
    if not isfinite(wet_bulb_c) or not -30 <= wet_bulb_c <= dry_bulb_c:
        raise ValueError("wet_bulb_c must be between -30 C and dry_bulb_c")

    thermal_load = facility_mw * 1000 * 24 * assumptions.utilization * assumptions.pue
    # h_fg ≈ 2501 - 2.361 T (kJ/kg); take 1 kg/L for screening, not equipment sizing.
    latent_heat_kj_kg = 2501 - 2.361 * max(0, wet_bulb_c)
    thermal_wue = 3600 / latent_heat_kj_kg * assumptions.evaporative_fraction_max
    warnings: tuple[str, ...] = ()
    if cooling_type == CoolingType.AIR_COOLED:
        thermal_wue = 0.0
    elif cooling_type == CoolingType.DIRECT_EVAPORATIVE and dry_bulb_c - wet_bulb_c < 3:
        warnings = ("low_wet_bulb_depression_requires_cooling_design_review",)
    if wet_bulb_c < 0 and cooling_type != CoolingType.AIR_COOLED:
        warnings += ("freezing_conditions_require_cooling_design_review",)

    return WaterBounds(
        min_mgd=0.0,
        max_mgd=thermal_wue * thermal_load / LITERS_PER_MILLION_GALLONS,
        thermal_load_kwh_day=thermal_load,
        max_liters_per_thermal_kwh=thermal_wue,
        max_site_wue_l_per_it_kwh=thermal_wue * assumptions.pue,
        assumptions=assumptions,
        warnings=warnings,
    )
