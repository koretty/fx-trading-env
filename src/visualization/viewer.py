from __future__ import annotations

from typing import Callable

from src.envs.fx_gym_env import FxGymEnv
from src.visualization.chart import Chart
from src.visualization.controller import Controller


class Viewer:
    """Debug viewer that operates as an env client via reset/step calls."""

    def __init__(
        self,
        env: FxGymEnv,
        chart: Chart,
        controller: Controller | None,
    ) -> None:
        self._env = env
        self._chart = chart

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
        frame = self._env.get_debug_frame()
        self._chart.render(
            visible_ohlc=frame.ohlc_window,
            visible_timestamps=frame.timestamps,
            current_step_global=frame.current_step,
            window_start_index=frame.window_start_index,
            status=frame.status,
        )

    def _build_key_bindings(self) -> dict[str, Callable[[], None]]:
        return {
            "right": self._hold_and_step,
            "home": self._reset,
            "a": self._open_long,
            "z": self._open_short,
            "x": self._close_position,
        }

    def _hold_and_step(self) -> None:
        self._env.step(self._env.ACTION_HOLD)

    def _reset(self) -> None:
        self._env.reset()

    def _open_long(self) -> None:
        self._env.step(self._env.ACTION_LONG)

    def _open_short(self) -> None:
        self._env.step(self._env.ACTION_SHORT)

    def _close_position(self) -> None:
        self._env.step(self._env.ACTION_CLOSE)
