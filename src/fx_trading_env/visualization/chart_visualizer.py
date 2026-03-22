from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np


class ChartVisualizer:
    """時系列の可視化を担当する描画専用クラス。"""

    def __init__(self, interactive: bool = True, pause_seconds: float = 0.05) -> None:
        self._interactive = interactive
        self._pause_seconds = pause_seconds

        self._figure, self._ax = plt.subplots(figsize=(10, 5))
        self._line_close, = self._ax.plot([], [], label="Close", linewidth=1.8)

        self._ax.set_title("OHLC Close Price")
        self._ax.set_xlabel("Timestep")
        self._ax.set_ylabel("Price")
        self._ax.grid(True, alpha=0.3)
        self._ax.legend(loc="upper left")

        if self._interactive:
            plt.ion()
            plt.show(block=False)

    def update(self, visible_data: np.ndarray, current_index: int) -> None:
        """
        現在までの可視データでグラフを更新する。

        Args:
            visible_data: `DataHandler.get_data_slice()` の戻り値
            current_index: 現在のインデックス（タイトル表示用）
        """
        if visible_data.ndim != 2 or visible_data.shape[1] != 4:
            raise ValueError(
                f"visible_data must be shape (N, 4), but got {visible_data.shape}."
            )

        close = visible_data[:, 3]
        x = np.arange(close.shape[0])

        self._line_close.set_data(x, close)
        self._ax.relim()
        self._ax.autoscale_view()
        self._ax.set_title(f"OHLC Close Price (t={current_index})")

        self._figure.canvas.draw_idle()
        if self._interactive:
            plt.pause(self._pause_seconds)

    def finalize(self) -> None:
        """描画終了処理。"""
        if self._interactive:
            plt.ioff()
        plt.show()
