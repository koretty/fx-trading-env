# Architecture Overview

このリポジトリは Gymnasium 互換のヘッドレス環境を中核にし、可視化はデバッグクライアントとして分離した構成です。

## モジュール一覧と役割

- src.main: エントリポイント。CLI解析、設定読み込み、FxGymEnv の組立て（csv_pathを渡して内部パーツを初期化）、必要に応じてデバッグViewer起動。
- src.utils.config_loader: AppConfig と設定読み込みロジック（YAML/JSON + CLI優先解決）。
- src.core.data_handler: CSV読み込み・正規化。読み込み時に NumPy 配列へ変換して高速アクセスAPIを提供。`get_ohlc_window` は範囲外stepで例外を送出し未来参照を禁止。
- src.core.engine: ポジション状態管理、スプレッド考慮の約定、uPnL/実現損益、証拠金維持率判定。
- src.core.features: Observation 生成プラグイン群（FeatureExtractor）。OHLC窓 + 口座/ポジション文脈を生成。
- src.core.rewards: 報酬計算プラグイン群（RewardFunction）。PnL差分ベースで報酬を算出。
- src.envs.fx_gym_env: Gymnasium互換環境。`__init__`で Engine / Feature / Reward / DataHandler を初期化し、reset/step/action_space/observation_space を提供。
- src.visualization.chart: デバッグ描画のみ（NumPy入力）。
- src.visualization.controller: キー入力を環境アクションへマッピング。
- src.visualization.viewer: Env クライアント。キー操作時に env.step(action) を呼ぶデバッグUI。

## 設計原則

- 主従関係: 外部エージェントが env.step(action) を呼び、環境が進む。
- 可視化の位置づけ: 学習本体から独立したオプショナルなデバッグ機能。
- 性能: ステップループでは pandas ではなく NumPy を利用。
- 拡張性: Feature/Reward を差し替え可能なプラグイン構造。

## クラス図（概要）

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
        -ndarray _ohlc
        -ndarray _timestamps
        +load()
        +get_price(step)
        +get_ohlc_window(step, window_size, pad)
        +get_timestamps_window(step, window_size, pad)
    }

    class TradingEngine {
        +open_long(price, units)
        +open_short(price, units)
        +close(price)
        +get_status(current_price)
        +unrealized_pnl(current_price)
        +maintenance_margin_ratio(current_price)
        +is_margin_call(current_price)
    }

    class FeatureExtractor {
        <<Protocol>>
        +observation_space
        +extract(data_handler, current_step, window_size, engine)
    }
    class OHLCWindowFeature

    class RewardFunction {
        <<Protocol>>
        +reset()
        +compute(prev_unrealized, next_unrealized, action, terminated, truncated)
    }
    class PnLDeltaReward

    class FxGymEnv {
        +reset(seed, options)
        +step(action)
        +render()
        +action_space
        +observation_space
    }

    class Chart {
        +render(visible_ohlc, visible_timestamps, current_step, window_start, status)
    }
    class Controller {
        +on_key_press(event)
    }
    class Viewer {
        +start()
        +redraw()
    }

    ConfigLoader --> AppConfig : produces
    FxGymEnv --> DataHandler : uses
    FxGymEnv --> TradingEngine : uses
    FxGymEnv --> FeatureExtractor : uses
    FxGymEnv --> RewardFunction : uses
    OHLCWindowFeature ..|> FeatureExtractor
    PnLDeltaReward ..|> RewardFunction
    Viewer --> FxGymEnv : client calls step/reset
    Viewer --> Chart : uses
    Viewer --> Controller : uses
    src.main ..> FxGymEnv : instantiates (with csv_path)
    src.main ..> Viewer : optional debug
```

補足:
- `TradingEngine` は mid価格入力から bid/ask を導出し、スプレッドを内包した約定価格で評価します。
- `FxGymEnv.step()` ではデータ末尾到達に加え、`is_margin_call` が `True` の場合も終了条件として扱います。
