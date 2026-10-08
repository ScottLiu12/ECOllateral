from datetime import date

import httpx
import numpy as np
import pandas as pd
import pytest

from src.ingestion.noaa_client import fetch_daily_weather, fetch_pdsi, wet_bulb_from_dewpoint
from src.ingestion.usgs_client import CFS_TO_MGD, fetch_huc_observations, station_series


def test_usgs_huc_pagination_conversion_and_quality():
    calls = []

    def handler(request):
        calls.append(request)
        if "monitoring-locations" in request.url.path:
            assert "02070010" in request.url.params["filter"]
            payload = {
                "features": [
                    {
                        "properties": {
                            "id": "USGS-01646500",
                            "hydrologic_unit_code": "020700100101",
                        },
                        "geometry": {"coordinates": [-77.1, 38.9]},
                    }
                ]
            }
        elif request.url.params.get("parameter_code") == "00060" or "offset" in request.url.params:
            second = "offset" in request.url.params
            payload = {
                "features": [
                    {
                        "properties": {
                            "value": "-999999" if second else "100",
                            "unit_of_measure": "ft^3/s",
                            "time": "2024-07-02" if second else "2024-07-01",
                            "approvals_status": ["Provisional"],
                            "qualifier": ["Estimated"],
                        }
                    }
                ]
            }
            if not second:
                payload["links"] = [{"rel": "next", "href": str(request.url) + "&offset=1"}]
        else:
            payload = {"features": []}
        return httpx.Response(200, json=payload)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        frame = fetch_huc_observations(client, "02070010", date(2024, 7, 1), date(2024, 7, 2))
    assert len(calls) == 5
    assert frame.iloc[0]["value"] == pytest.approx(100 * CFS_TO_MGD)
    assert np.isnan(frame.iloc[1]["value"])
    assert "Estimated" in frame.iloc[0]["quality"]
    assert station_series(frame).iloc[0, 0] == pytest.approx(100 * CFS_TO_MGD)


def test_noaa_native_units_missing_values_and_pdsi():
    def handler(request):
        if "services" in request.url.path:
            assert request.url.params["units"] == "standard"
            return httpx.Response(
                200,
                json=[
                    {"DATE": "2024-07-01", "TEMP": "86", "DEWP": "68", "PRCP": "0.5"},
                    {"DATE": "2024-07-02", "TEMP": "9999.9", "DEWP": "9999.9", "PRCP": "99.99"},
                ],
            )
        if request.url.path.endswith("/"):
            return httpx.Response(200, text='href="climdiv-pdsidv-v1.0.0-20240801"')
        return httpx.Response(200, text="4401052024 " + " ".join(["-2.5"] * 12))

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        weather = fetch_daily_weather(client, "72403093738", date(2024, 7, 1), date(2024, 7, 2))
        pdsi = fetch_pdsi(client, "4401", date(2024, 7, 1), date(2024, 7, 31))
    assert weather.iloc[0]["dry_bulb_c"] == pytest.approx(30)
    assert weather.iloc[0]["precipitation_mm"] == pytest.approx(12.7)
    assert 20 < weather.iloc[0]["wet_bulb_c"] < 30
    assert weather.iloc[1][["dry_bulb_c", "wet_bulb_c", "precipitation_mm"]].isna().all()
    assert pdsi.iloc[0]["pdsi"] == -2.5


def test_wet_bulb_rejects_extrapolation_and_handles_saturation():
    wet, _ = wet_bulb_from_dewpoint(pd.Series([30.0, 60.0, 30.0]), pd.Series([30.0, 40.0, 31.0]))
    assert wet[0] == 30
    assert wet[1:].isna().all()


def test_api_failure_is_not_an_empty_dataset():
    with httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(503))) as client:
        with pytest.raises(httpx.HTTPStatusError):
            fetch_daily_weather(client, "72403093738", date(2024, 7, 1), date(2024, 7, 2))
