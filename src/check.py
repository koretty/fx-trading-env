from __future__ import annotations

import argparse
import sys
from pathlib import Path


# Support direct execution: python src/check.py
if __package__ is None or __package__ == "":
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from gymnasium.utils.env_checker import check_env

from src.envs.fx_gym_env import FxGymEnv
from src.utils.config_loader import ConfigLoader


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Gymnasium API compatibility check")
    parser.add_argument("--config", type=str, default=None, help="Path to YAML/JSON config file")
    parser.add_argument("--csv", type=str, default=None, help="Path to OHLC CSV file")
    parser.add_argument("--window-size", type=int, default=None, help="Observation window size")
    parser.add_argument("--max-episode-steps", type=int, default=None, help="Optional truncation step count")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    config = ConfigLoader.load(
        config_path=args.config,
        csv_path_override=args.csv,
        window_size_override=args.window_size,
    )

    env = FxGymEnv(
        csv_path=config.csv_path,
        window_size=config.window_size,
        max_episode_steps=args.max_episode_steps,
    )

    check_env(env)
    print("check_env: OK")


if __name__ == "__main__":
    main()
