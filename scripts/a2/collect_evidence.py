# Standalone runner adds the repository root before importing project modules.
# ruff: noqa: E402
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.api.app import create_app
from src.demo import create_demo, hydrology_data
from src.grounding.chunking import PermitSection, chunk_section
from src.grounding.generator import generate_summary
from src.grounding.store import PermitStore
from src.models.missingness import analyze_missingness
from src.models.regression import ForecastModel


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    output = ROOT / "docs/a2/evidence"
    output.mkdir(parents=True, exist_ok=True)
    demo = ROOT / "data/processed/demo"
    if not (demo / "model.joblib").exists():
        create_demo(demo)
    model = ForecastModel.load(demo / "model.joblib")
    write_json(
        output / "benchmark.json", {"data_kind": model.data_kind, "benchmark": model.benchmark}
    )
    rows = []
    for technology, report in model.benchmark.items():
        for candidate, metrics in report["candidates"].items():
            rows.append(
                {
                    "cooling_type": technology,
                    "candidate": candidate,
                    "selected": candidate == report["selected"],
                    **metrics["test_bounded"],
                    "calibration_rmse_mgd": metrics["calibration"]["rmse_mgd"],
                }
            )
    pd.DataFrame(rows).to_csv(output / "regression-comparison.csv", index=False)
    pd.DataFrame(
        [
            {
                "cooling_type": technology,
                "nominal_coverage": 0.9,
                "test_coverage": report["test_interval90_coverage"],
                "test_rows": report["split"]["test_rows"],
                "data_kind": model.data_kind,
                "radius_mgd": report["interval90_radius_mgd"],
            }
            for technology, report in model.benchmark.items()
        ]
    ).to_csv(output / "interval-coverage.csv", index=False)

    with TestClient(create_app(data_dir=demo)) as client:
        request = {
            "facility_mw": 40,
            "cooling_type": "cooling_tower",
            "huc8": "02070010",
            "seasonal_target": 7,
        }
        response = client.post("/forecast", json=request)
        response.raise_for_status()
        write_json(output / "forecast.json", response.json())
        write_json(output / "forecast-request.json", request)

    features = pd.DataFrame(
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
    clipping = []
    for forced_value in (-1.0, 1_000_000.0):
        injected = replace(
            model.models["cooling_tower"],
            estimator=SimpleNamespace(
                predict=lambda frame, value=forced_value: np.full(len(frame), value)
            ),
        )
        injected_model = replace(model, models={**model.models, "cooling_tower": injected})
        prediction = injected_model.predict(features, "cooling_tower")[0]
        assert "constraint_violation" in prediction.warnings
        clipping.append({"case": "fault_injected_estimator_output", **asdict(prediction)})
    write_json(
        output / "constraint-failure-cases.json",
        {"inputs": features.iloc[0].to_dict(), "cases": clipping},
    )

    def permit(document_id, huc8=(), **scope):
        return PermitSection(
            document_id=document_id,
            title="Example cooling water permit",
            section="IV.B",
            text="Example cooling water withdrawals require reporting.",
            source_url="https://example.org/a2-permit",
            huc8=huc8,
            is_example=True,
            **scope,
        )

    local = permit("local-huc", ("02070010",))
    wrong = permit("other-huc", ("02070011",))
    coordinate = permit("coordinate-only", latitude=38.9, longitude=-77.1, radius_km=5)
    cases = []
    for name, documents, geography in [
        ("huc_filter", [wrong, local], {"huc8": "02070010"}),
        ("wrong_huc_empty", [local], {"huc8": "99999999"}),
        ("huc_only_coordinate_permit_excluded", [coordinate], {"huc8": "02070010"}),
        (
            "coordinates_coordinate_permit_included",
            [coordinate],
            {"huc8": "02070010", "latitude": 38.9, "longitude": -77.1},
        ),
    ]:
        store = PermitStore([chunk for document in documents for chunk in chunk_section(document)])
        excerpts = store.retrieve("cooling water withdrawal permit reporting", top_k=1, **geography)
        narrative = generate_summary(0.20433878898620605, excerpts)
        cases.append(
            {
                "case": name,
                "query_geography": geography,
                "retrieved_document_ids": [item.chunk.permit.document_id for item in excerpts],
                "scores": [item.score for item in excerpts],
                **asdict(narrative),
            }
        )
    assert [case["retrieved_document_ids"] for case in cases] == [
        ["local-huc"],
        [],
        [],
        ["coordinate-only"],
    ]
    write_json(
        output / "retrieval-cases.json", {"corpus_kind": "fictional_test_sections", "cases": cases}
    )

    stations, coordinates, features = hydrology_data()
    research = ROOT / "data/processed/research"
    if not (research / "missingness_summary.csv").exists():
        result = analyze_missingness(
            stations,
            "target",
            coordinates,
            features,
            lambda frame: np.array(
                [p.predicted_mgd for p in model.predict(frame, "cooling_tower")]
            ),
        )
        result.summary.to_csv(output / "missingness-summary.csv", index=False)
    else:
        shutil.copyfile(research / "missingness_summary.csv", output / "missingness-summary.csv")
    for original, name in [
        ("missingness_sensitivity.png", "missingness-sensitivity.png"),
        ("missingness_band90.png", "missingness-band90.png"),
        ("groundwater_reconstruction.csv", "groundwater-reconstruction.csv"),
    ]:
        if (research / original).exists():
            shutil.copyfile(research / original, output / name)
    biased = stations.copy()
    biased[["adjacent_a", "adjacent_b"]] += 100
    diagnostic = analyze_missingness(
        biased,
        "target",
        coordinates,
        features,
        lambda frame: frame.historical_streamflow_mgd.to_numpy() * 0.01,
        rates=(0.4,),
        repeats=20,
    )
    diagnostic.summary.to_csv(output / "biased-donor-diagnostic.csv", index=False)

    tests = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True
    )
    (output / "test-results.txt").write_text(tests.stdout + tests.stderr, encoding="utf-8")
    if tests.returncode:
        raise RuntimeError("project tests failed; inspect evidence/test-results.txt")
    live = ROOT / "data/processed/live-smoke/environment.csv"
    if live.exists():
        shutil.copyfile(live, output / "live-ingestion-snapshot.csv")
    sources = [
        ROOT / "src/models/regression.py",
        ROOT / "src/rules/thermodynamic.py",
        ROOT / "src/models/missingness.py",
        ROOT / "src/grounding/store.py",
        ROOT / "src/api/app.py",
        ROOT / "src/demo.py",
    ]
    records = [
        {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in sources
    ]
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name != "manifest.json":
            records.append(
                {
                    "path": "evidence/" + path.name,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

    write_json(
        output / "manifest.json",
        {
            "review_date": "2026-10-07",
            "implementation_snapshot_commit": git("rev-parse", "125aa40"),
            "capture_commit": git("rev-parse", "HEAD"),
            "python": sys.version,
            "seed": 42,
            "data_kind": "synthetic_benchmark_and_research",
            "live_ingestion_scope": (
                "two-day parser smoke test; climate division is not spatially validated"
            ),
            "diagnostic_predictor": (
                "biased-donor test uses 0.01 * streamflow; not the fitted ML model"
            ),
            "files": records,
        },
    )
    print(f"Curated evidence saved to {output}")


if __name__ == "__main__":
    main()
