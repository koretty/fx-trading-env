from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np
from gymnasium import spaces  # type: ignore[reportMissingImports]

from src.core.data_handler import DataHandler
from src.core.engine import TradingEngine


class FeatureExtractor(Protocol):
    @property
    def observation_space(self) -> spaces.Box:
        ...

    def extract(
        self,
        data_handler: DataHandler,
        current_step: int,
        window_size: int,
        engine: TradingEngine,
    ) -> np.ndarray:
        ...


@dataclass(frozen=True)
class OHLCWindowFeature:
    """Builds a fixed-size flat observation from OHLC window and position context."""

    window_size: int

    def __post_init__(self) -> None:
        if self.window_size <= 0:
            raise ValueError("window_size must be > 0")

        obs_dim = self.window_size * 4 + 4
        object.__setattr__(
            self,
            "_observation_space",
            spaces.Box(
                low=-np.inf,
                high=np.inf,
                shape=(obs_dim,),
                dtype=np.float32,
            ),
        )

    @property
    def observation_space(self) -> spaces.Box:
        return self._observation_space

    def extract(
        self,
        data_handler: DataHandler,
        current_step: int,
        window_size: int,
        engine: TradingEngine,
    ) -> np.ndarray:
        if window_size != self.window_size:
            raise ValueError(
                f"window_size mismatch: feature={self.window_size}, requested={window_size}"
            )

        ohlc_window, _ = data_handler.get_ohlc_window(current_step=current_step, window_size=window_size, pad=True)
        last_close = max(float(ohlc_window[-1, 3]), 1e-8)

        normalized_window = (ohlc_window / last_close) - 1.0
        flat = normalized_window.astype(np.float32, copy=False).reshape(-1)

        position = engine.get_position()
        side_value = 0.0
        if position.side.value == "LONG":
            side_value = 1.0
        elif position.side.value == "SHORT":
            side_value = -1.0

        current_price = data_handler.get_price(current_step)
        unrealized = np.float32(engine.unrealized_pnl(current_price))
        spread = np.float32(engine.spread)
        margin_ratio = engine.maintenance_margin_ratio(current_price)
        if np.isinf(margin_ratio):
            margin_signal = np.float32(1.0)
        else:
            # Ratio >= 100 is generally safe; clip to keep the scale bounded.
            margin_signal = np.float32(np.clip((margin_ratio / 100.0) - 1.0, -5.0, 5.0))

        context = np.array([np.float32(side_value), unrealized, spread, margin_signal], dtype=np.float32)
        return np.concatenate((flat, context), axis=0)
