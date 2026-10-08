import argparse
import json
import os
from datetime import date
from pathlib import Path

import httpx
import numpy as np
import pandas as pd

from src.demo import create_demo
from src.grounding.store import PermitStore
from src.ingestion.noaa_client import fetch_daily_weather, fetch_pdsi
from src.ingestion.snapshots import monthly_snapshots
from src.ingestion.usgs_client import fetch_huc_observations
from src.models.missingness import analyze_missingness
from src.models.regression import ForecastModel, train_model
from src.rules.thermodynamic import CoolingType, ThermalAssumptions


def ingest(args: argparse.Namespace) -> None:
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        water = fetch_huc_observations(
            client,
            args.huc8,
            args.start,
            args.end,
            api_key=os.environ.get("USGS_API_KEY"),
            station_ids=tuple(dict.fromkeys([args.flow_station, *args.station])),
        )
        weather = fetch_daily_weather(client, args.noaa_station, args.start, args.end)
        pdsi = fetch_pdsi(client, args.climate_division, args.start, args.end)
    args.raw_output.mkdir(parents=True, exist_ok=True)
    prefix = args.raw_output / f"{args.huc8}_{args.start}_{args.end}"
    water.to_csv(str(prefix) + "_water.csv", index=False)
    weather.to_csv(str(prefix) + "_weather.csv", index=False)
    pdsi.to_csv(str(prefix) + "_pdsi.csv", index=False)
    daily, snapshots = monthly_snapshots(water, weather, pdsi, args.huc8, args.flow_station)
    args.output.mkdir(parents=True, exist_ok=True)
    daily.to_csv(args.output / f"{args.huc8}_daily.csv", index=False)
    output_path = args.output / "environment.csv"
    if output_path.exists():
        previous = pd.read_csv(output_path, dtype={"huc8": str})
        snapshots = pd.concat([previous, snapshots]).drop_duplicates(["huc8", "month"], keep="last")
    snapshots.to_csv(output_path, index=False)
    print(
        f"Saved {len(water)} water records, {len(weather)} weather records, "
        f"and {len(snapshots)} HUC/month snapshots to {args.output}"
    )


def train(args: argparse.Namespace) -> None:
    records = pd.read_csv(args.input)
    model = train_model(
        records,
        data_kind=args.data_kind,
        assumptions=ThermalAssumptions(
            pue=args.pue,
            utilization=args.utilization,
            evaporative_fraction_max=args.evaporative_fraction_max,
        ),
    )
    args.output.mkdir(parents=True, exist_ok=True)
    model.save(args.output / "model.joblib")
    report = {"data_kind": model.data_kind, "benchmark": model.benchmark}
    serialized = json.dumps(report, indent=2, allow_nan=False) + "\n"
    (args.output / "benchmark.json").write_text(serialized, encoding="utf-8")
    print(serialized)


def sensitivity(args: argparse.Namespace) -> None:
    stations = pd.read_csv(args.stations, index_col="date", parse_dates=["date"])
    coordinates = pd.read_csv(args.coordinates, index_col="station_id")
    features = pd.read_csv(args.features, index_col="date", parse_dates=["date"])
    model = ForecastModel.load(args.model)

    def predict(frame: pd.DataFrame) -> np.ndarray:
        return np.array(
            [prediction.predicted_mgd for prediction in model.predict(frame, args.cooling)]
        )

    result = analyze_missingness(
        stations, args.target, coordinates, features, predict, repeats=args.repeats, seed=args.seed
    )
    args.output.mkdir(parents=True, exist_ok=True)
    result.summary.to_csv(args.output / "missingness_summary.csv", index=False)
    result.bands.to_csv(args.output / "missingness_bands.csv", index=False)
    print(f"Model data kind: {model.data_kind}")
    print(result.summary.to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="ECOllateral ingestion, training, and research")
    commands = parser.add_subparsers(dest="command", required=True)
    demo_parser = commands.add_parser("demo", help="create explicitly synthetic, offline artifacts")
    demo_parser.add_argument("--output", type=Path, default=Path("data/processed/demo"))

    ingestion = commands.add_parser("ingest", help="fetch public USGS/NOAA observations")
    ingestion.add_argument("--huc8", required=True)
    ingestion.add_argument("--flow-station", required=True, help="e.g. USGS-01646500")
    ingestion.add_argument(
        "--station", action="append", default=[], help="additional station in HUC"
    )
    ingestion.add_argument("--noaa-station", required=True, help="11-digit GSOD ID")
    ingestion.add_argument("--climate-division", required=True, help="4-digit NOAA division ID")
    ingestion.add_argument("--start", type=date.fromisoformat, required=True)
    ingestion.add_argument("--end", type=date.fromisoformat, required=True)
    ingestion.add_argument("--output", type=Path, default=Path("data/processed"))
    ingestion.add_argument("--raw-output", type=Path, default=Path("data/raw"))

    training = commands.add_parser("train", help="train on labeled facility consumption records")
    training.add_argument("--input", type=Path, required=True)
    training.add_argument("--output", type=Path, default=Path("data/processed"))
    training.add_argument("--data-kind", choices=["observed", "synthetic"], default="observed")
    training.add_argument("--pue", type=float, default=1.2)
    training.add_argument("--utilization", type=float, default=1.0)
    training.add_argument("--evaporative-fraction-max", type=float, default=1.0)

    indexing = commands.add_parser(
        "index-permits", help="index extracted permit sections from JSONL"
    )
    indexing.add_argument("--input", type=Path, required=True)
    indexing.add_argument("--output", type=Path, default=Path("data/processed/permits"))

    research = commands.add_parser("sensitivity", help="repeat drought-only streamflow masking")
    research.add_argument("--stations", type=Path, required=True)
    research.add_argument("--coordinates", type=Path, required=True)
    research.add_argument("--features", type=Path, required=True)
    research.add_argument("--model", type=Path, required=True)
    research.add_argument("--target", required=True)
    research.add_argument(
        "--cooling", choices=[value.value for value in CoolingType], default="cooling_tower"
    )
    research.add_argument("--repeats", type=int, default=50)
    research.add_argument("--seed", type=int, default=42)
    research.add_argument("--output", type=Path, default=Path("data/processed/research"))

    args = parser.parse_args()
    if args.command == "demo":
        create_demo(args.output)
        print(f"Synthetic demo artifacts saved to {args.output}. These are not field validation.")
    elif args.command == "ingest":
        ingest(args)
    elif args.command == "train":
        train(args)
    elif args.command == "index-permits":
        store = PermitStore.from_jsonl(args.input)
        store.save(args.output)
        print(f"Indexed {len(store.chunks)} chunks in {args.output}")
    elif args.command == "sensitivity":
        sensitivity(args)


if __name__ == "__main__":
    main()
