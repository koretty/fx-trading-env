from __future__ import annotations

import argparse

from fx_trading_env.app.simulation import run_simulation


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FX OHLC Data Handler + Time-series Visualizer"
    )
    parser.add_argument(
        "csv",
        type=str,
        help="Path to CSV that includes OHLC columns: Open, High, Low, Close",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.05,
        help="Pause seconds between frames for interactive plotting.",
    )
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    run_simulation(csv_path=args.csv, interval_seconds=args.interval)


if __name__ == "__main__":
    main()
