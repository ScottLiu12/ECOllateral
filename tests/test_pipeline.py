from datetime import date

import httpx
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from src.api.app import ForecastResources, create_app
from src.grounding.chunking import PermitSection, chunk_section
from src.grounding.store import PermitStore
from src.ingestion.noaa_client import fetch_daily_weather, fetch_pdsi
from src.ingestion.snapshots import EnvironmentData, monthly_snapshots
from src.ingestion.usgs_client import fetch_huc_observations


@pytest.fixture
def resources(fitted_model):
    def upstream(request):
        if "monitoring-locations" in request.url.path:
            return httpx.Response(
                200,
                json={
                    "features": [
                        {
                            "properties": {
                                "id": "USGS-01646500",
                                "hydrologic_unit_code": "02070010",
                            },
                            "geometry": {"coordinates": [-77.1, 38.9]},
                        }
                    ]
                },
            )
        if "daily/items" in request.url.path:
            if request.url.params["parameter_code"] != "00060":
                return httpx.Response(200, json={"features": []})
            return httpx.Response(
                200,
                json={
                    "features": [
                        {
                            "properties": {
                                "time": f"2024-07-0{day}",
                                "value": "100",
                                "unit_of_measure": "ft^3/s",
                                "approval_status": "Approved",
                            }
                        }
                        for day in (1, 2)
                    ]
                },
            )
        if "services/data" in request.url.path:
            return httpx.Response(
                200,
                json=[
                    {"DATE": f"2024-07-0{day}", "TEMP": "86", "DEWP": "68", "PRCP": "0.0"}
                    for day in (1, 2)
                ],
            )
        if request.url.path.endswith("/"):
            return httpx.Response(200, text="climdiv-pdsidv-v1.0.0-20240801")
        return httpx.Response(200, text="4401052024 " + " ".join(["-3"] * 12))

    start, end = date(2024, 7, 1), date(2024, 7, 2)
    with httpx.Client(transport=httpx.MockTransport(upstream)) as client:
        water = fetch_huc_observations(client, "02070010", start, end)
        weather = fetch_daily_weather(client, "72403093738", start, end)
        pdsi = fetch_pdsi(client, "4401", start, end)
    _, monthly = monthly_snapshots(water, weather, pdsi, "02070010", "USGS-01646500")
    assert monthly.streamflow_record_count.tolist() == [2]
    assert "Approved" in water.iloc[0].quality
    permits = PermitStore(
        chunk_section(
            PermitSection(
                document_id="test-permit",
                title="Test water permit",
                section="3.2",
                text="Cooling water withdrawals require monthly reporting.",
                source_url="https://example.org/test-permit",
                huc8=("02070010",),
                is_example=True,
            )
        )
    )
    return ForecastResources(fitted_model, EnvironmentData(monthly), permits)


def payload(**overrides):
    return {
        "facility_mw": 40,
        "cooling_type": "cooling_tower",
        "huc8": "02070010",
        "seasonal_target": 7,
        **overrides,
    }


def test_ingestion_rules_regression_grounding_and_http_response(resources):
    with TestClient(create_app(resources)) as client:
        response = client.post("/forecast", json=payload())
        assert response.status_code == 200, response.text
        result = response.json()
        bounds = result["thermodynamic_bounds"]
        assert bounds["min_mgd"] <= result["predicted_collateral_stress_mgd"] <= bounds["max_mgd"]
        assert result["heldout_r2"] > 0.8
        assert result["citations"][0]["section"] == "3.2"
        assert "monthly reporting" in result["regulatory_risk_summary"]
        assert result["model_data_kind"] == "synthetic"
        assert client.get("/health").json()["status"] == "ready"


@pytest.mark.parametrize(
    "overrides",
    [
        {"facility_mw": -1},
        {"huc8": "123"},
        {"seasonal_target": 13},
        {"huc8": None},
        {"latitude": 38.9},
        {"typo": "unexpected"},
        {"huc8": "99999999"},
        {"seasonal_target": 1},
    ],
)
def test_bad_or_unavailable_requests_are_rejected(resources, overrides):
    with TestClient(create_app(resources)) as client:
        assert client.post("/forecast", json=payload(**overrides)).status_code == 422


def test_coordinates_resolve_only_nearby_representative_station(resources):
    with TestClient(create_app(resources)) as client:
        result = client.post("/forecast", json=payload(huc8=None, latitude=38.9, longitude=-77.1))
        assert result.status_code == 200
        assert "coordinates_resolved_to_nearest_station_huc" in result.json()["warnings"]
        assert (
            client.post("/forecast", json=payload(huc8=None, latitude=0, longitude=0)).status_code
            == 422
        )


def test_missing_artifacts_returns_actionable_503(tmp_path):
    with TestClient(create_app(data_dir=tmp_path)) as client:
        assert client.get("/health").json()["status"] == "unconfigured"
        assert client.post("/forecast", json=payload()).status_code == 503


def test_empty_grounding_is_visible(resources):
    resources.permits = PermitStore([])
    with TestClient(create_app(resources)) as client:
        result = client.post("/forecast", json=payload()).json()
        assert result["citations"] == []
        assert "no_regulatory_grounding" in result["warnings"]


def test_snapshot_duplicate_rows_rejected(resources):
    records = resources.environment.records
    with pytest.raises(ValueError, match="one row"):
        EnvironmentData(pd.concat([records, records]))


def test_coordinate_scoped_permit_needs_facility_coordinates(resources):
    resources.permits = PermitStore(chunk_section(PermitSection(
        document_id="coordinate-permit", title="Local cooling water permit", section="1",
        text="Cooling water withdrawals require reporting.",
        source_url="https://example.org/local-permit", latitude=38.9, longitude=-77.1,
        radius_km=5, is_example=True,
    )))
    with TestClient(create_app(resources)) as client:
        assert client.post("/forecast", json=payload()).json()["citations"] == []
        result = client.post("/forecast", json=payload(latitude=38.9, longitude=-77.1)).json()
        assert result["citations"][0]["document_id"] == "coordinate-permit"
