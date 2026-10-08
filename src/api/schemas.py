from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.rules.thermodynamic import CoolingType


class ForecastRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    facility_mw: float = Field(ge=0, le=10_000, description="Installed IT capacity, MW")
    cooling_type: CoolingType
    huc8: str | None = Field(default=None, pattern=r"^[0-9]{8}$")
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    seasonal_target: int = Field(ge=1, le=12, description="Target calendar month, 1–12")

    @model_validator(mode="after")
    def check_location(self) -> Self:
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be supplied together")
        if self.huc8 is None and self.latitude is None:
            raise ValueError("provide huc8 or latitude and longitude")
        return self


class BoundsResponse(BaseModel):
    min_mgd: float
    max_mgd: float
    thermal_load_kwh_day: float
    max_liters_per_thermal_kwh: float
    max_site_wue_l_per_it_kwh: float
    pue: float
    utilization: float
    evaporative_fraction_max: float


class PredictionInterval(BaseModel):
    nominal_coverage: float = 0.9
    min_mgd: float
    max_mgd: float
    method: str = "split_conformal_absolute_residuals"


class CitationResponse(BaseModel):
    document_id: str
    title: str
    section: str
    source_url: str
    excerpt: str
    is_example: bool


class ForecastResponse(BaseModel):
    huc8: str
    seasonal_target: int
    thermodynamic_bounds: BoundsResponse
    predicted_collateral_stress_mgd: float = Field(
        description="Daily on-site cooling consumption proxy; not a municipal stress index"
    )
    raw_prediction_mgd: float
    heldout_r2: float | None = Field(
        description="Held-out fit metric, not a confidence probability"
    )
    prediction_interval90: PredictionInterval
    model_name: str
    model_data_kind: str
    environment_data_kind: str
    source_period_start: str
    source_period_end: str
    regulatory_risk_summary: str
    citations: list[CitationResponse]
    warnings: list[str]
