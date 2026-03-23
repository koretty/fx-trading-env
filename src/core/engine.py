from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PositionSide(str, Enum):
    """Trading side representation for UI and future RL integration."""

    FLAT = "FLAT"
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class PositionState:
    """Current position state managed by the engine."""

    side: PositionSide = PositionSide.FLAT
    entry_price: float | None = None
    units: float = 1.0


class TradingEngine:
    """Minimal position engine separated from rendering and input concerns."""

    def __init__(self) -> None:
        self._position = PositionState()

    def open_long(self, price: float, units: float = 1.0) -> None:
        self._position = PositionState(side=PositionSide.LONG, entry_price=price, units=units)

    def open_short(self, price: float, units: float = 1.0) -> None:
        self._position = PositionState(side=PositionSide.SHORT, entry_price=price, units=units)

    def close(self) -> None:
        self._position = PositionState()

    def get_position(self) -> PositionState:
        return self._position

    def unrealized_pnl(self, current_price: float) -> float:
        if self._position.side == PositionSide.FLAT or self._position.entry_price is None:
            return 0.0
        if self._position.side == PositionSide.LONG:
            return (current_price - self._position.entry_price) * self._position.units
        return (self._position.entry_price - current_price) * self._position.units

    def get_status(self, current_price: float) -> dict[str, float | str | None]:
        position = self.get_position()
        return {
            "side": position.side.value,
            "entry_price": position.entry_price,
            "units": position.units,
            "unrealized_pnl": self.unrealized_pnl(current_price),
        }
