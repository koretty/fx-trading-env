from __future__ import annotations

from pathlib import Path

import numpy as np

from fx_trading_env.data.csv_loader import load_ohlc_from_csv
from fx_trading_env.domain.ohlc_columns import OhlcColumns


class DataHandler:
    """
    OHLC時系列データの読込と安全なインデックス管理を担当する。

    - データ内部表現: numpy.ndarray shape=(N, 4)
    - 列順: [Open, High, Low, Close]
    - ルックアヘッド防止: `current_index` より未来への公開アクセスは提供しない
    """

    def __init__(self, csv_path: str | Path, columns: OhlcColumns = OhlcColumns()) -> None:
        self._csv_path = Path(csv_path)
        self._columns = columns
        self._data: np.ndarray = load_ohlc_from_csv(self._csv_path, self._columns)
        self.current_index: int = 0

    @property
    def data_length(self) -> int:
        """全データ件数を返す。"""
        return int(self._data.shape[0])

    def reset(self, start_index: int = 0) -> None:
        """
        現在インデックスを初期化する。

        Args:
            start_index: 再開位置。0 <= start_index < N を満たす必要がある。

        Raises:
            IndexError: 範囲外の開始位置を指定した場合。
        """
        if not 0 <= start_index < self.data_length:
            raise IndexError(
                f"start_index={start_index} is out of bounds for data length {self.data_length}."
            )
        self.current_index = start_index

    def step(self) -> int:
        """
        インデックスを1進める。

        Returns:
            更新後の current_index

        Raises:
            IndexError: 末尾を超えて進めようとした場合。
        """
        next_index = self.current_index + 1
        if next_index >= self.data_length:
            raise IndexError("No more data available. Reached the end of OHLC series.")
        self.current_index = next_index
        return self.current_index

    def get_current_price(self) -> float:
        """
        現在インデックスのClose価格を返す。

        Raises:
            IndexError: current_index が範囲外の場合。
        """
        if not 0 <= self.current_index < self.data_length:
            raise IndexError(
                f"current_index={self.current_index} is out of bounds for data length {self.data_length}."
            )
        close_col = 3
        return float(self._data[self.current_index, close_col])

    def get_data_slice(self) -> np.ndarray:
        """
        現在時点までのデータのみを返す。

        Returns:
            `self._data[:current_index + 1]` のコピー

        Raises:
            IndexError: current_index が範囲外の場合。
        """
        if not 0 <= self.current_index < self.data_length:
            raise IndexError(
                f"current_index={self.current_index} is out of bounds for data length {self.data_length}."
            )
        return self._data[: self.current_index + 1].copy()
