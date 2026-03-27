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
    action_cost: float = 0.0
    margin_call_penalty: float = 0.0
    scale: float = 1.0

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
        reward = float(next_unrealized - prev_unrealized) * float(self.scale)
        if action != 0:
            reward -= float(self.action_cost)

        if terminated and not truncated:
            reward += float(self.terminal_bonus)

        if terminated and next_unrealized < prev_unrealized:
            reward -= float(self.margin_call_penalty)

        return reward
