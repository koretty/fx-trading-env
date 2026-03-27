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
    entry_mid_price: float | None = None
    entry_price: float | None = None
    units: float = 1.0


class TradingEngine:
    """Minimal position engine separated from rendering and input concerns."""

    def __init__(
        self,
        *,
        spread: float = 0.0002,
        contract_size: float = 1.0,
        leverage: float = 25.0,
        initial_balance: float = 10000.0,
        maintenance_margin_threshold: float = 100.0,
    ) -> None:
        if spread < 0.0:
            raise ValueError("spread must be >= 0")
        if contract_size <= 0.0:
            raise ValueError("contract_size must be > 0")
        if leverage <= 0.0:
            raise ValueError("leverage must be > 0")
        if initial_balance <= 0.0:
            raise ValueError("initial_balance must be > 0")
        if maintenance_margin_threshold <= 0.0:
            raise ValueError("maintenance_margin_threshold must be > 0")

        self._position = PositionState()
        self._spread = float(spread)
        self._contract_size = float(contract_size)
        self._leverage = float(leverage)
        self._balance = float(initial_balance)
        self._initial_balance = float(initial_balance)
        self._maintenance_margin_threshold = float(maintenance_margin_threshold)
        self._last_realized_pnl = 0.0

    def open_long(self, price: float, units: float = 1.0) -> None:
        checked_price = self._validate_price(price)
        checked_units = self._validate_units(units)
        self.close(price=checked_price)
        ask = self._ask(checked_price)
        self._position = PositionState(
            side=PositionSide.LONG,
            entry_mid_price=checked_price,
            entry_price=ask,
            units=checked_units,
        )

    def open_short(self, price: float, units: float = 1.0) -> None:
        checked_price = self._validate_price(price)
        checked_units = self._validate_units(units)
        self.close(price=checked_price)
        bid = self._bid(checked_price)
        self._position = PositionState(
            side=PositionSide.SHORT,
            entry_mid_price=checked_price,
            entry_price=bid,
            units=checked_units,
        )

    def close(self, price: float | None = None) -> float:
        realized = 0.0
        if self._position.side != PositionSide.FLAT and price is not None:
            realized = self.unrealized_pnl(price)
            self._balance += realized

        self._last_realized_pnl = float(realized)
        self._position = PositionState()
        return float(realized)

    def reset_account(self) -> None:
        self._position = PositionState()
        self._balance = float(self._initial_balance)
        self._last_realized_pnl = 0.0

    def get_position(self) -> PositionState:
        return self._position

    @property
    def spread(self) -> float:
        return self._spread

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def last_realized_pnl(self) -> float:
        return self._last_realized_pnl

    def unrealized_pnl(self, current_price: float) -> float:
        checked_price = self._validate_price(current_price)
        if self._position.side == PositionSide.FLAT or self._position.entry_price is None:
            return 0.0

        units = self._position.units * self._contract_size
        if self._position.side == PositionSide.LONG:
            exit_price = self._bid(checked_price)
            return (exit_price - self._position.entry_price) * units

        exit_price = self._ask(checked_price)
        return (self._position.entry_price - exit_price) * units

    def used_margin(self) -> float:
        if self._position.side == PositionSide.FLAT:
            return 0.0
        if self._position.entry_mid_price is None:
            return 0.0
        notional = self._position.entry_mid_price * self._position.units * self._contract_size
        return notional / self._leverage

    def maintenance_margin_ratio(self, current_price: float) -> float:
        margin = self.used_margin()
        if margin <= 0.0:
            return float("inf")
        equity = self._balance + self.unrealized_pnl(current_price)
        return (equity / margin) * 100.0

    def is_margin_call(self, current_price: float) -> bool:
        if self._position.side == PositionSide.FLAT:
            return False
        return self.maintenance_margin_ratio(current_price) < self._maintenance_margin_threshold

    def get_status(self, current_price: float) -> dict[str, float | str | bool | None]:
        position = self.get_position()
        margin_ratio = self.maintenance_margin_ratio(current_price)
        return {
            "side": position.side.value,
            "entry_mid_price": position.entry_mid_price,
            "entry_price": position.entry_price,
            "units": position.units,
            "spread": self._spread,
            "balance": self._balance,
            "last_realized_pnl": self._last_realized_pnl,
            "unrealized_pnl": self.unrealized_pnl(current_price),
            "used_margin": self.used_margin(),
            "maintenance_margin_ratio": margin_ratio,
            "is_margin_call": self.is_margin_call(current_price),
        }

    def _ask(self, mid_price: float) -> float:
        return float(mid_price + (self._spread * 0.5))

    def _bid(self, mid_price: float) -> float:
        return float(mid_price - (self._spread * 0.5))

    def _validate_price(self, price: float) -> float:
        checked = float(price)
        if checked <= 0.0:
            raise ValueError(f"price must be > 0: got {checked}")
        return checked

    def _validate_units(self, units: float) -> float:
        checked = float(units)
        if checked <= 0.0:
            raise ValueError(f"units must be > 0: got {checked}")
        return checked
