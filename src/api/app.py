import os
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

from src.api.schemas import ForecastRequest, ForecastResponse
from src.grounding.generator import generate_summary
from src.grounding.store import PermitStore
from src.ingestion.snapshots import EnvironmentData
from src.models.regression import ForecastModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class ForecastResources:
    model: ForecastModel
    environment: EnvironmentData
    permits: PermitStore


def forecast(request: ForecastRequest, resources: ForecastResources) -> ForecastResponse:
    snapshot = resources.environment.resolve(
        request.seasonal_target, request.huc8, request.latitude, request.longitude
    )
    row = snapshot.values
    features = pd.DataFrame([{**row, "facility_mw": request.facility_mw}])
    prediction = resources.model.predict(features, request.cooling_type)[0]
    excerpts = resources.permits.retrieve(
        f"{request.cooling_type.value.replace('_', ' ')} cooling water withdrawal allocation "
        "permit drought municipal watershed reporting cap",
        huc8=row["huc8"],
        latitude=request.latitude,
        longitude=request.longitude,
    )
    narrative = generate_summary(prediction.predicted_mgd, excerpts)
    bound = prediction.bounds
    warnings = list(dict.fromkeys((*snapshot.warnings, *prediction.warnings, *narrative.warnings)))
    if row["data_kind"] == "synthetic":
        warnings.append("synthetic_environment_not_observed_conditions")
    return ForecastResponse(
        huc8=row["huc8"],
        seasonal_target=request.seasonal_target,
        thermodynamic_bounds={
            "min_mgd": bound.min_mgd,
            "max_mgd": bound.max_mgd,
            "thermal_load_kwh_day": bound.thermal_load_kwh_day,
            "max_liters_per_thermal_kwh": bound.max_liters_per_thermal_kwh,
            "max_site_wue_l_per_it_kwh": bound.max_site_wue_l_per_it_kwh,
            **asdict(bound.assumptions),
        },
        predicted_collateral_stress_mgd=prediction.predicted_mgd,
        raw_prediction_mgd=prediction.raw_mgd,
        heldout_r2=prediction.heldout_r2,
        prediction_interval90={
            "min_mgd": prediction.interval90_min_mgd,
            "max_mgd": prediction.interval90_max_mgd,
        },
        model_name=resources.model.models[request.cooling_type.value].name,
        model_data_kind=resources.model.data_kind,
        environment_data_kind=row["data_kind"],
        source_period_start=str(row["source_period_start"]),
        source_period_end=str(row["source_period_end"]),
        regulatory_risk_summary=narrative.summary,
        citations=[asdict(citation) for citation in narrative.citations],
        warnings=warnings,
    )


def create_app(
    resources: ForecastResources | None = None, *, data_dir: Path | None = None
) -> FastAPI:
    data_dir = data_dir or Path(
        os.environ.get("ECOLLATERAL_DATA_DIR", str(PROJECT_ROOT / "data" / "processed"))
    )

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        if resources is not None:
            application.state.resources = resources
        elif (data_dir / "model.joblib").exists() and (data_dir / "environment.csv").exists():
            permit_path = data_dir / "permits"
            application.state.resources = ForecastResources(
                ForecastModel.load(data_dir / "model.joblib"),
                EnvironmentData.load(data_dir / "environment.csv"),
                PermitStore.load(permit_path)
                if (permit_path / "metadata.joblib").exists()
                else PermitStore([]),
            )
        else:
            application.state.resources = None
        yield

    application = FastAPI(title="ECOllateral", version="0.1.0", lifespan=lifespan)

    @application.get("/health")
    def health() -> dict:
        available = getattr(application.state, "resources", None)
        return {
            "status": "ready" if available else "unconfigured",
            "model_data_kind": available.model.data_kind if available else None,
        }

    @application.post("/forecast", response_model=ForecastResponse)
    def forecast_endpoint(request: ForecastRequest) -> ForecastResponse:
        available = getattr(application.state, "resources", None)
        if available is None:
            raise HTTPException(503, "Train a model and ingest environment data before forecasting")
        try:
            return forecast(request, available)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error

    return application


app = create_app()
