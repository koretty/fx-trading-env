from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from fx_trading_env.domain.ohlc_columns import OhlcColumns


def load_ohlc_from_csv(csv_path: Path, columns: OhlcColumns) -> np.ndarray:
    """CSVからOHLC列を読み込み、floatの(N, 4)配列を返す。"""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    missing = [col for col in columns.as_list() if col not in df.columns]
    if missing:
        raise ValueError(
            f"Required OHLC columns are missing from CSV: {missing}. "
            f"Available columns: {list(df.columns)}"
        )

    ohlc_df = df[columns.as_list()].copy()
    if ohlc_df.isnull().any().any():
        raise ValueError("OHLC data contains NaN values. Clean the CSV before loading.")

    ohlc_np = ohlc_df.to_numpy(dtype=np.float64)

    if ohlc_np.ndim != 2 or ohlc_np.shape[1] != 4:
        raise ValueError(f"Loaded OHLC data must be shape (N, 4), but got {ohlc_np.shape}.")

    if ohlc_np.shape[0] == 0:
        raise ValueError("OHLC data is empty.")

    return ohlc_np
