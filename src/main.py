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
from src.envs.fx_gym_env import FxGymEnv
from src.utils.config_loader import ConfigLoader
from src.visualization.chart import Chart
from src.visualization.viewer import Viewer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FX Gymnasium environment runner")
    parser.add_argument("--config", type=str, default=None, help="Path to YAML/JSON config file")
    parser.add_argument("--csv", type=str, default=None, help="Path to OHLC CSV file")
    parser.add_argument("--window-size", type=int, default=None, help="Visible candle count")
    parser.add_argument("--initial-step", type=int, default=None, help="Initial replay step")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["headless", "viewer"],
        default="viewer",
        help="Run mode: headless (env smoke run) or viewer (debug UI)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=100,
        help="Step count for headless mode",
    )
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

    env = FxGymEnv(
        data_handler=data_handler,
        window_size=config.window_size,
    )

    if args.mode == "headless":
        _, _ = env.reset(options={"start_step": config.initial_step})
        total_reward = 0.0
        for _ in range(max(1, args.steps)):
            _, reward, terminated, truncated, _ = env.step(env.ACTION_HOLD)
            total_reward += reward
            if terminated or truncated:
                break
        print(f"headless finished: step={env.current_step}, total_reward={total_reward:.6f}")
        return

    chart = Chart()
    viewer = Viewer(
        env=env,
        chart=chart,
        controller=None,
    )
    env.reset(options={"start_step": min(config.initial_step, len(data_handler) - 1)})
    viewer.start()


if __name__ == "__main__":
    main()
