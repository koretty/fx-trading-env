from __future__ import annotations

from typing import Callable


class Controller:
    """Maps key inputs to actions only. No chart/data logic here."""

    def __init__(
        self,
        key_bindings: dict[str, Callable[[], None]],
        redraw_callback: Callable[[], None],
    ) -> None:
        self._key_bindings = key_bindings
        self._redraw_callback = redraw_callback

    def on_key_press(self, event: object) -> None:
        key = getattr(event, "key", None)
        if key is None:
            return

        action = self._key_bindings.get(key)
        if action is None:
            return

        action()
        self._redraw_callback()
