from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OhlcColumns:
    """CSV内のOHLC列名を定義する設定オブジェクト。"""

    open: str = "Open"
    high: str = "High"
    low: str = "Low"
    close: str = "Close"

    def as_list(self) -> list[str]:
        return [self.open, self.high, self.low, self.close]
