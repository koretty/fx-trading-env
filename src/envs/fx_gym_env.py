from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import gymnasium as gym  # type: ignore[reportMissingImports]
import numpy as np
from gymnasium import spaces  # type: ignore[reportMissingImports]

from src.core.data_handler import DataHandler
from src.core.engine import PositionSide, TradingEngine
from src.core.features import FeatureExtractor, OHLCWindowFeature
from src.core.rewards import PnLDeltaReward, RewardFunction


@dataclass(frozen=True)
class EnvDebugFrame:
    ohlc_window: np.ndarray
    timestamps: np.ndarray
    current_step: int
    window_start_index: int
    status: dict[str, float | str | bool | None]


class FxGymEnv(gym.Env[np.ndarray, int]):
    """Gymnasium-compatible headless FX trading environment."""

    metadata = {"render_modes": ["human"], "render_fps": 15}

    ACTION_HOLD = 0
    ACTION_LONG = 1
    ACTION_SHORT = 2
    ACTION_CLOSE = 3

    def __init__(
        self,
        csv_path: str | Path | None = None,
        data_handler: DataHandler | None = None,
        engine: TradingEngine | None = None,
        window_size: int = 120,
        feature_extractor: FeatureExtractor | None = None,
        reward_function: RewardFunction | None = None,
        max_episode_steps: int | None = None,
    ) -> None:
        if window_size <= 0:
            raise ValueError("window_size must be > 0")

        if data_handler is None:
            if csv_path is None:
                raise ValueError("Either csv_path or data_handler must be provided")
            created_data_handler = DataHandler(csv_path)
            created_data_handler.load()
            self._data_handler = created_data_handler
        else:
            self._data_handler = data_handler
            try:
                len(self._data_handler)
            except RuntimeError:
                self._data_handler.load()

        self._window_size = int(window_size)

        self._engine = engine or TradingEngine()
        self._feature_extractor = feature_extractor or OHLCWindowFeature(window_size=self._window_size)
        self._reward_function = reward_function or PnLDeltaReward()

        if len(self._data_handler) <= 1:
            raise ValueError("Dataset must contain at least 2 rows for stepping")

        self.action_space = spaces.Discrete(4)
        self.observation_space = self._feature_extractor.observation_space

        self._current_step = self._window_size - 1
        self._episode_start_step = self._window_size - 1
        self._episode_elapsed_steps = 0
        self._max_episode_steps = max_episode_steps

    @property
    def current_step(self) -> int:
        return self._current_step

    @property
    def window_size(self) -> int:
        return self._window_size

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        super().reset(seed=seed)

        self._engine.reset_account()
        self._reward_function.reset()
        self._episode_elapsed_steps = 0

        requested_step = self._window_size - 1
        if options and "start_step" in options:
            requested_step = int(options["start_step"])

        self._current_step = max(self._window_size - 1, min(requested_step, len(self._data_handler) - 1))
        self._episode_start_step = self._current_step

        obs = self._build_observation()
        info = self._build_info(action=self.ACTION_HOLD)
        return obs, info

    def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        if not self.action_space.contains(action):
            raise ValueError(f"Invalid action: {action}")

        price_before = self._data_handler.get_price(self._current_step)
        prev_unrealized = self._engine.unrealized_pnl(price_before)

        self._apply_action(action=action, price=price_before)

        terminated_by_end = self._current_step >= len(self._data_handler) - 1
        if not terminated_by_end:
            self._current_step += 1

        self._episode_elapsed_steps += 1

        truncated = False
        if self._max_episode_steps is not None and self._episode_elapsed_steps >= self._max_episode_steps:
            truncated = True

        price_after = self._data_handler.get_price(self._current_step)
        next_unrealized = self._engine.unrealized_pnl(price_after)
        terminated_by_margin_call = self._engine.is_margin_call(price_after)
        terminated = terminated_by_end or terminated_by_margin_call

        reward = self._reward_function.compute(
            prev_unrealized=prev_unrealized,
            next_unrealized=next_unrealized,
            action=action,
            terminated=terminated,
            truncated=truncated,
        )

        obs = self._build_observation()
        info = self._build_info(action=action)
        return obs, float(reward), bool(terminated), bool(truncated), info

    def render(self) -> EnvDebugFrame:
        return self.get_debug_frame()

    def get_debug_frame(self) -> EnvDebugFrame:
        ohlc_window, start = self._data_handler.get_ohlc_window(
            current_step=self._current_step,
            window_size=self._window_size,
            pad=False,
        )
        timestamps, _ = self._data_handler.get_timestamps_window(
            current_step=self._current_step,
            window_size=self._window_size,
            pad=False,
        )
        status = self._engine.get_status(current_price=self._data_handler.get_price(self._current_step))
        return EnvDebugFrame(
            ohlc_window=ohlc_window,
            timestamps=timestamps,
            current_step=self._current_step,
            window_start_index=start,
            status=status,
        )

    def _apply_action(self, action: int, price: float) -> None:
        if action == self.ACTION_HOLD:
            return

        if action == self.ACTION_LONG:
            self._engine.open_long(price)
            return

        if action == self.ACTION_SHORT:
            self._engine.open_short(price)
            return

        if action == self.ACTION_CLOSE:
            self._engine.close(price=price)
            return

    def _build_observation(self) -> np.ndarray:
        obs = self._feature_extractor.extract(
            data_handler=self._data_handler,
            current_step=self._current_step,
            window_size=self._window_size,
            engine=self._engine,
        )
        return np.asarray(obs, dtype=np.float32)

    def _build_info(self, action: int) -> dict[str, Any]:
        price = self._data_handler.get_price(self._current_step)
        position = self._engine.get_position()
        return {
            "current_step": self._current_step,
            "action": int(action),
            "price": float(price),
            "position_side": str(position.side.value),
            "entry_mid_price": None if position.entry_mid_price is None else float(position.entry_mid_price),
            "entry_price": None if position.entry_price is None else float(position.entry_price),
            "spread": float(self._engine.spread),
            "balance": float(self._engine.balance),
            "last_realized_pnl": float(self._engine.last_realized_pnl),
            "unrealized_pnl": float(self._engine.unrealized_pnl(price)),
            "maintenance_margin_ratio": float(self._engine.maintenance_margin_ratio(price)),
            "is_margin_call": bool(self._engine.is_margin_call(price)),
            "episode_elapsed_steps": self._episode_elapsed_steps,
            "episode_start_step": self._episode_start_step,
        }

    def get_engine_position_side(self) -> PositionSide:
        return self._engine.get_position().side
