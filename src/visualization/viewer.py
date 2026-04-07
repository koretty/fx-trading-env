from __future__ import annotations

from typing import Callable

from src.envs.fx_gym_env import FxGymEnv
from src.visualization.chart import Chart
from src.visualization.controller import Controller


class Viewer:
    """Debug viewer that operates as an env client via reset/step calls."""

    AUTO_PLAY_INTERVAL_MS = 1000

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
        self._is_auto_playing = False
        self._auto_play_timer = self._chart.figure.canvas.new_timer(interval=self.AUTO_PLAY_INTERVAL_MS)
        self._auto_play_timer.add_callback(self._on_auto_play_tick)

    def start(self) -> None:
        self._chart.figure.canvas.mpl_connect("key_press_event", self._controller.on_key_press)
        self._chart.figure.canvas.mpl_connect("close_event", self._on_close)
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
            " ": self._toggle_auto_play,
            "space": self._toggle_auto_play,
            "home": self._reset,
            "a": self._open_long,
            "z": self._open_short,
            "x": self._close_position,
        }

    def _step(self, action: int) -> None:
        _, _, terminated, truncated, _ = self._env.step(action)
        if terminated or truncated:
            self._stop_auto_play()

    def _hold_and_step(self) -> None:
        self._step(self._env.ACTION_HOLD)

    def _reset(self) -> None:
        self._stop_auto_play()
        self._env.reset()

    def _open_long(self) -> None:
        self._step(self._env.ACTION_LONG)

    def _open_short(self) -> None:
        self._step(self._env.ACTION_SHORT)

    def _close_position(self) -> None:
        self._step(self._env.ACTION_CLOSE)

    def _toggle_auto_play(self) -> None:
        if self._is_auto_playing:
            self._stop_auto_play()
            return

        self._is_auto_playing = True
        self._auto_play_timer.start()

    def _stop_auto_play(self) -> None:
        if not self._is_auto_playing:
            return

        self._is_auto_playing = False
        self._auto_play_timer.stop()

    def _on_auto_play_tick(self, *_: object) -> None:
        self._hold_and_step()
        self.redraw()

    def _on_close(self, _: object) -> None:
        self._stop_auto_play()
