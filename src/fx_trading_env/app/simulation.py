from __future__ import annotations

from pathlib import Path

from fx_trading_env.services.data_handler import DataHandler
from fx_trading_env.visualization.chart_visualizer import ChartVisualizer


def run_simulation(csv_path: str | Path, interval_seconds: float = 0.05) -> None:
    """
    実行例:
    1) CSVを読み込む
    2) DataHandlerを初期化
    3) stepをループで進める
    4) ChartVisualizerで逐次描画する
    """
    handler = DataHandler(csv_path=csv_path)
    handler.reset(start_index=0)

    visualizer = ChartVisualizer(interactive=True, pause_seconds=interval_seconds)

    # 初期時点を描画
    visualizer.update(handler.get_data_slice(), handler.current_index)

    while True:
        try:
            handler.step()
            visible = handler.get_data_slice()
            visualizer.update(visible, handler.current_index)
            _ = handler.get_current_price()
        except IndexError:
            break

    visualizer.finalize()
