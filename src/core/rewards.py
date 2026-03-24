from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class RewardFunction(Protocol):
    def reset(self) -> None:
        ...

    def compute(
        self,
        prev_unrealized: float,
        next_unrealized: float,
        action: int,
        terminated: bool,
        truncated: bool,
    ) -> float:
        ...


@dataclass
class PnLDeltaReward:
    """Reward = change in unrealized PnL with optional terminal bonus/penalty."""

    terminal_bonus: float = 0.0

    def reset(self) -> None:
        return None

    def compute(
        self,
        prev_unrealized: float,
        next_unrealized: float,
        action: int,
        terminated: bool,
        truncated: bool,
    ) -> float:
        reward = float(next_unrealized - prev_unrealized)
        if terminated and not truncated:
            reward += float(self.terminal_bonus)
        return reward
