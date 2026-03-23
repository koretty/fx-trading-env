from __future__ import annotations

import argparse
import sys
from pathlib import Path


# Support direct execution: python src/main.py
if __package__ is None or __package__ == "":
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from src.core.data_handler import DataHandler
from src.core.engine import TradingEngine
from src.utils.config_loader import ConfigLoader
from src.visualization.chart import Chart
from src.visualization.viewer import Viewer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FX chart step viewer")
    parser.add_argument("--config", type=str, default=None, help="Path to JSON config file")
    parser.add_argument("--csv", type=str, default=None, help="Path to OHLC CSV file")
    parser.add_argument("--window-size", type=int, default=None, help="Visible candle count")
    parser.add_argument("--initial-step", type=int, default=None, help="Initial replay step")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    config = ConfigLoader.load(
        config_path=args.config,
        csv_path_override=args.csv,
        window_size_override=args.window_size,
        initial_step_override=args.initial_step,
    )

    data_handler = DataHandler(config.csv_path)
    data_handler.load()

    chart = Chart()
    engine = TradingEngine()

    viewer = Viewer(
        data_handler=data_handler,
        chart=chart,
        controller=None,
        engine=engine,
        initial_step=min(config.initial_step, len(data_handler) - 1),
        window_size=config.window_size,
    )
    viewer.start()


if __name__ == "__main__":
    main()
