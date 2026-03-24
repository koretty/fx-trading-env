# Architecture Overview

このリポジトリのアーキテクチャ概要。

## モジュール一覧と役割

- `src.main`: エントリポイント。CLI解析、設定読み込み、各コンポーネントの組立て。
- `src.utils.config_loader`: `AppConfig` と設定読み込みロジック（JSON/CLIの優先解決）。
- `src.core.data_handler`: CSV読み込み・正規化・時系列データ提供。
- `src.core.engine`: 取引ポジション管理と PnL 計算（ビジネスロジック）。
- `src.visualization.chart`: 描画のみを担当（matplotlib）。
- `src.visualization.controller`: キー入力→アクションのマッピング。
- `src.visualization.viewer`: コンポーネント合成、再生制御、UIループ。

## クラス図（概要）

以下は主要クラスの関係（テキストベース、Mermaid）。

```mermaid
classDiagram
    class AppConfig {
        +Path csv_path
        +int window_size
        +int initial_step
    }
    class ConfigLoader {
        +load(...)
    }

    class DataHandler {
        -Path _csv_path
        -DataFrame _data
        +load()
        +get_price(step)
        +get_visible_window(step, window_size)
    }

    class PositionSide
    class PositionState {
        +PositionSide side
        +float entry_price
        +float units
    }
    class TradingEngine {
        -PositionState _position
        +open_long(price, units)
        +open_short(price, units)
        +close()
        +get_status(current_price)
        +unrealized_pnl(current_price)
    }

    class ChartStyle
    class Chart {
        -ChartStyle _style
        +render(visible_df, current_step_global, window_start_index, status)
    }

    class Controller {
        -key_bindings
        +on_key_press(event)
    }

    class ViewerState {
        +int current_step
    }
    class Viewer {
        -DataHandler _data_handler
        -Chart _chart
        -Controller _controller
        -TradingEngine _engine
        -ViewerState _state
        +start()
        +redraw()
    }

    Viewer --> DataHandler : uses
    Viewer --> Chart : uses
    Viewer --> Controller : uses
    Viewer --> TradingEngine : uses
    Chart --> ChartStyle : uses
    TradingEngine --> PositionState : owns
    PositionState --> PositionSide : uses
    ConfigLoader --> AppConfig : produces
    src.main ..> Viewer : instantiates
```
