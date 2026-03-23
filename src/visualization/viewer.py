from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from src.core.data_handler import DataHandler
from src.core.engine import TradingEngine
from src.visualization.chart import Chart
from src.visualization.controller import Controller


@dataclass
class ViewerState:
    """Mutable state for replay position."""

    current_step: int


class Viewer:
    """Composes data, engine, chart, and controller."""

    def __init__(
        self,
        data_handler: DataHandler,
        chart: Chart,
        controller: Controller | None,
        engine: TradingEngine,
        initial_step: int,
        window_size: int,
    ) -> None:
        if window_size <= 0:
            raise ValueError("window_size must be > 0")

        self._data_handler = data_handler
        self._chart = chart
        self._engine = engine
        self._window_size = window_size

        max_index = len(self._data_handler) - 1
        self._state = ViewerState(current_step=max(0, min(initial_step, max_index)))

        self._controller = controller or Controller(
            key_bindings=self._build_key_bindings(),
            redraw_callback=self.redraw,
        )

    def start(self) -> None:
        self._chart.figure.canvas.mpl_connect("key_press_event", self._controller.on_key_press)
        self.redraw()

        # Import locally so test code can instantiate Viewer without an active GUI backend.
        import matplotlib.pyplot as plt

        plt.show()

    def redraw(self) -> None:
        visible_df, window_start = self._data_handler.get_visible_window(
            self._state.current_step,
            self._window_size,
        )
        current_price = self._data_handler.get_price(self._state.current_step)
        status = self._engine.get_status(current_price=current_price)
        self._chart.render(
            visible_df=visible_df,
            current_step_global=self._state.current_step,
            window_start_index=window_start,
            status=status,
        )

    def _build_key_bindings(self) -> dict[str, Callable[[], None]]:
        return {
            "right": self._step_forward,
            "left": self._step_backward,
            "home": self._jump_start,
            "end": self._jump_end,
            "a": self._open_long,
            "z": self._open_short,
            "x": self._close_position,
        }

    def _step_forward(self) -> None:
        self._state.current_step = min(self._state.current_step + 1, len(self._data_handler) - 1)

    def _step_backward(self) -> None:
        self._state.current_step = max(self._state.current_step - 1, 0)

    def _jump_start(self) -> None:
        self._state.current_step = 0

    def _jump_end(self) -> None:
        self._state.current_step = len(self._data_handler) - 1

    def _open_long(self) -> None:
        price = self._data_handler.get_price(self._state.current_step)
        self._engine.open_long(price)

    def _open_short(self) -> None:
        price = self._data_handler.get_price(self._state.current_step)
        self._engine.open_short(price)

    def _close_position(self) -> None:
        self._engine.close()
