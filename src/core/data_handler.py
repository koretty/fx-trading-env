from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


class DataHandler:
    """Loads market data once and serves fast NumPy slices for simulation."""

    def __init__(self, csv_path: str | Path) -> None:
        self._csv_path = Path(csv_path)
        self._data: Optional[pd.DataFrame] = None
        self._timestamps: Optional[np.ndarray] = None
        self._ohlc: Optional[np.ndarray] = None
        self._close: Optional[np.ndarray] = None

    @property
    def data(self) -> pd.DataFrame:
        if self._data is None:
            raise RuntimeError("Data is not loaded. Call load() first.")
        return self._data

    @property
    def ohlc(self) -> np.ndarray:
        if self._ohlc is None:
            raise RuntimeError("Data is not loaded. Call load() first.")
        return self._ohlc

    @property
    def timestamps(self) -> np.ndarray:
        if self._timestamps is None:
            raise RuntimeError("Data is not loaded. Call load() first.")
        return self._timestamps

    def load(self) -> pd.DataFrame:
        if not self._csv_path.exists():
            raise FileNotFoundError(f"CSV not found: {self._csv_path}")

        raw = pd.read_csv(self._csv_path, sep=None, engine="python")
        normalized_columns = {
            col: col.strip().strip("<>").lower() for col in raw.columns
        }
        raw = raw.rename(columns=normalized_columns)

        required = {"date", "time", "open", "high", "low", "close"}
        missing = required - set(raw.columns)
        if missing:
            raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

        timestamp_raw = raw["date"].astype(str) + " " + raw["time"].astype(str)
        timestamp_dt = pd.to_datetime(
            timestamp_raw,
            errors="coerce",
        )
        if timestamp_dt.isna().any():
            raise ValueError("Failed to parse date/time columns in CSV.")

        df = pd.DataFrame(
            {
                "timestamp": timestamp_raw,
                "timestamp_dt": timestamp_dt,
                "open": pd.to_numeric(raw["open"], errors="coerce"),
                "high": pd.to_numeric(raw["high"], errors="coerce"),
                "low": pd.to_numeric(raw["low"], errors="coerce"),
                "close": pd.to_numeric(raw["close"], errors="coerce"),
            }
        ).dropna()

        if df.empty:
            raise ValueError("No valid OHLC rows were loaded from CSV.")

        self._data = (
            df.sort_values("timestamp_dt", ascending=True)
            .drop(columns=["timestamp_dt"])
            .reset_index(drop=True)
        )

        # Convert once to compact NumPy arrays to avoid pandas overhead in step loops.
        self._timestamps = self._data["timestamp"].to_numpy(copy=True)
        self._ohlc = self._data[["open", "high", "low", "close"]].to_numpy(dtype=np.float32, copy=True)
        self._close = self._ohlc[:, 3]
        return self._data

    def __len__(self) -> int:
        return len(self.ohlc)

    def get_price(self, step: int) -> float:
        if self._close is None:
            raise RuntimeError("Data is not loaded. Call load() first.")
        return float(self._close[self._clamp_step(step)])

    def get_ohlc_row(self, step: int) -> np.ndarray:
        return self.ohlc[self._clamp_step(step)]

    def get_ohlc_window(self, current_step: int, window_size: int, pad: bool = False) -> tuple[np.ndarray, int]:
        if window_size <= 0:
            raise ValueError("window_size must be > 0")

        current_step = self._clamp_step(current_step)
        start = max(0, current_step - window_size + 1)
        visible = self.ohlc[start : current_step + 1]

        if not pad or len(visible) == window_size:
            return visible, start

        pad_len = window_size - len(visible)
        head = np.repeat(visible[:1], repeats=pad_len, axis=0)
        return np.concatenate((head, visible), axis=0), start

    def get_timestamps_window(self, current_step: int, window_size: int, pad: bool = False) -> tuple[np.ndarray, int]:
        if window_size <= 0:
            raise ValueError("window_size must be > 0")

        current_step = self._clamp_step(current_step)
        start = max(0, current_step - window_size + 1)
        visible = self.timestamps[start : current_step + 1]

        if not pad or len(visible) == window_size:
            return visible, start

        pad_len = window_size - len(visible)
        head = np.repeat(visible[:1], repeats=pad_len)
        return np.concatenate((head, visible), axis=0), start

    def get_visible_window(self, current_step: int, window_size: int) -> tuple[pd.DataFrame, int]:
        if window_size <= 0:
            raise ValueError("window_size must be > 0")

        current_step = self._clamp_step(current_step)
        start = max(0, current_step - window_size + 1)
        visible = self.data.iloc[start : current_step + 1].copy()
        return visible, start

    def _clamp_step(self, step: int) -> int:
        if len(self.ohlc) == 0:
            raise ValueError("Loaded dataset is empty")
        return max(0, min(int(step), len(self.ohlc) - 1))
