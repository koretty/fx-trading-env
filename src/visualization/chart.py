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
        visible_df: pd.DataFrame,
        current_step_global: int,
        window_start_index: int,
        status: dict[str, Any],
    ) -> None:
        self._ax_price.clear()
        self._ax_info.clear()
        self._ax_info.axis("off")

        self._draw_candlesticks(visible_df)
        self._draw_current_marker(current_step_global, window_start_index, len(visible_df))
        self._draw_status_panel(visible_df.iloc[-1], current_step_global, status)

        self._ax_price.set_title("FX Candlestick Viewer (No Lookahead)")
        self._ax_price.set_ylabel("Price")
        self._ax_price.grid(True, alpha=0.25)
        self._fig.canvas.draw_idle()

    def _draw_candlesticks(self, df: pd.DataFrame) -> None:
        width = 0.6

        for idx, row in enumerate(df.itertuples(index=False)):
            open_p = float(row.open)
            high_p = float(row.high)
            low_p = float(row.low)
            close_p = float(row.close)

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

        tick_positions = self._build_hourly_tick_positions(df)
        tick_labels = [str(df.iloc[i]["timestamp"]) for i in tick_positions]
        self._ax_price.set_xticks(tick_positions)
        self._ax_price.set_xticklabels(tick_labels, rotation=25, ha="right")

    def _build_hourly_tick_positions(self, df: pd.DataFrame) -> np.ndarray:
        parsed = pd.to_datetime(df["timestamp"], errors="coerce")

        # Prefer exact hourly marks (:00:00) for readability.
        hourly_positions = np.where(
            (parsed.dt.minute == 0) & (parsed.dt.second == 0)
        )[0]

        if len(hourly_positions) == 0:
            return np.linspace(0, len(df) - 1, num=min(8, len(df)), dtype=int)

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

    def _draw_status_panel(self, current_row: pd.Series, current_step: int, status: dict[str, Any]) -> None:
        current_price = float(current_row["close"])
        entry = status.get("entry_price")
        entry_text = "-" if entry is None else f"{float(entry):.5f}"

        info = (
            f"step={current_step}  "
            f"time={current_row['timestamp']}  "
            f"close={current_price:.5f}  "
            f"position={status.get('side', 'N/A')}  "
            f"entry={entry_text}  "
            f"uPnL={float(status.get('unrealized_pnl', 0.0)):.5f}"
        )
        hint = "Keys: Left/Right=step, A=long, Z=short, X=close, Home/End=jump"

        self._ax_info.text(0.01, 0.62, info, fontsize=10, va="center", ha="left")
        self._ax_info.text(0.01, 0.18, hint, fontsize=9, va="center", ha="left", color="#444444")
