from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle


@dataclass(frozen=True)
class ChartStyle:
    """Chart style configuration to keep rendering configurable."""

    up_color: str = "#2ca02c"
    down_color: str = "#d62728"
    wick_color: str = "#444444"
    marker_color: str = "#1f77b4"


class Chart:
    """Responsible only for chart rendering."""

    def __init__(self, style: ChartStyle | None = None) -> None:
        self._style = style or ChartStyle()
        self._fig: Figure
        self._ax_price: Axes
        self._ax_info: Axes
        self._fig, (self._ax_price, self._ax_info) = plt.subplots(
            2,
            1,
            figsize=(13, 7),
            gridspec_kw={"height_ratios": [5, 1]},
            constrained_layout=True,
        )
        self._ax_info.axis("off")

    @property
    def figure(self) -> Figure:
        return self._fig

    def render(
        self,
        visible_ohlc: np.ndarray,
        visible_timestamps: np.ndarray,
        current_step_global: int,
        window_start_index: int,
        status: dict[str, Any],
    ) -> None:
        self._ax_price.clear()
        self._ax_info.clear()
        self._ax_info.axis("off")

        self._draw_candlesticks(visible_ohlc, visible_timestamps)
        self._draw_current_marker(current_step_global, window_start_index, len(visible_ohlc))
        self._draw_status_panel(visible_ohlc[-1], str(visible_timestamps[-1]), current_step_global, status)

        self._ax_price.set_title("FX Candlestick Viewer (No Lookahead)")
        self._ax_price.set_ylabel("Price")
        self._ax_price.grid(True, alpha=0.25)
        self._fig.canvas.draw_idle()

    def _draw_candlesticks(self, ohlc: np.ndarray, timestamps: np.ndarray) -> None:
        width = 0.6

        for idx, row in enumerate(ohlc):
            open_p = float(row[0])
            high_p = float(row[1])
            low_p = float(row[2])
            close_p = float(row[3])

            candle_color = self._style.up_color if close_p >= open_p else self._style.down_color

            self._ax_price.vlines(
                idx,
                low_p,
                high_p,
                color=self._style.wick_color,
                linewidth=1.0,
                zorder=1,
            )

            body_bottom = min(open_p, close_p)
            body_height = max(abs(close_p - open_p), 1e-6)
            rect = Rectangle(
                (idx - width / 2, body_bottom),
                width,
                body_height,
                facecolor=candle_color,
                edgecolor=candle_color,
                linewidth=1.0,
                zorder=2,
            )
            self._ax_price.add_patch(rect)

        tick_positions = self._build_hourly_tick_positions(timestamps)
        tick_labels = [str(timestamps[i]) for i in tick_positions]
        self._ax_price.set_xticks(tick_positions)
        self._ax_price.set_xticklabels(tick_labels, rotation=25, ha="right")

    def _build_hourly_tick_positions(self, timestamps: np.ndarray) -> np.ndarray:
        parsed = pd.to_datetime(timestamps, errors="coerce")
        parsed_index = pd.DatetimeIndex(parsed)
        minutes = parsed_index.minute
        seconds = parsed_index.second

        # Prefer exact hourly marks (:00:00) for readability.
        hourly_positions = np.where((minutes == 0) & (seconds == 0))[0]

        if len(hourly_positions) == 0:
            return np.linspace(0, len(timestamps) - 1, num=min(8, len(timestamps)), dtype=int)

        return hourly_positions

    def _draw_current_marker(self, current_step_global: int, window_start_index: int, visible_len: int) -> None:
        marker_x = current_step_global - window_start_index
        if 0 <= marker_x < visible_len:
            self._ax_price.axvline(
                marker_x,
                color=self._style.marker_color,
                linestyle="--",
                linewidth=1.5,
                alpha=0.85,
                label="current",
            )
            self._ax_price.legend(loc="upper left")

    def _draw_status_panel(self, current_row: np.ndarray, current_timestamp: str, current_step: int, status: dict[str, Any]) -> None:
        current_price = float(current_row[3])
        entry = status.get("entry_price")
        entry_text = "-" if entry is None else f"{float(entry):.5f}"

        info = (
            f"step={current_step}  "
            f"time={current_timestamp}  "
            f"close={current_price:.5f}  "
            f"position={status.get('side', 'N/A')}  "
            f"entry={entry_text}  "
            f"uPnL={float(status.get('unrealized_pnl', 0.0)):.5f}"
        )
        hint = "Keys: Right=hold/step, Space=auto hold(1s toggle), A=long+step, Z=short+step, X=close+step, Home=reset"

        self._ax_info.text(0.01, 0.62, info, fontsize=10, va="center", ha="left")
        self._ax_info.text(0.01, 0.18, hint, fontsize=9, va="center", ha="left", color="#444444")
