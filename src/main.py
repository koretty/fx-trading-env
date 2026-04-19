from __future__ import annotations

import argparse
import sys
from pathlib import Path


# Support direct execution: python src/main.py
if __package__ is None or __package__ == "":
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

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

    env = FxGymEnv(
        csv_path=config.csv_path,
        window_size=config.window_size,
    )

    if args.mode == "headless":
        _, _ = env.reset(options={"start_step": config.initial_step})
        total_reward = 0.0
        last_info: dict[str, object] = {}
        for _ in range(max(1, args.steps)):
            _, reward, terminated, truncated, info = env.step(env.ACTION_HOLD)
            total_reward += reward
            last_info = info
            if terminated or truncated:
                break

        print(
            "headless finished: "
            f"step={env.current_step}, "
            f"total_reward={total_reward:.6f}, "
            f"closed_trades={int(last_info.get('closed_trades', 0))}, "
            f"win_rate={float(last_info.get('win_rate', 0.0)):.2f}%, "
            f"max_dd={float(last_info.get('episode_max_drawdown', 0.0)):.6f}, "
            f"max_dd_pct={float(last_info.get('episode_max_drawdown_pct', 0.0)):.4f}%, "
            f"equity={float(last_info.get('equity', 0.0)):.2f}"
        )
        return

    chart = Chart()
    viewer = Viewer(
        env=env,
        chart=chart,
        controller=None,
    )
    env.reset(options={"start_step": config.initial_step})
    viewer.start()


if __name__ == "__main__":
    main()
