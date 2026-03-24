# Data Flow

データの流れ（入力 → 処理 → 出力）を示します。

- 入力: CSV（OHLC）
- 前処理: `DataHandler.load()` が CSV を読み込み、正規化して DataFrame を生成
- 表示: `Viewer` が `DataHandler.get_visible_window()` / `get_price()` を呼び、`Chart.render()` に渡す
- ロジック: ユーザー操作で `Viewer` が `TradingEngine` を操作（open/close）し、`get_status()` を返す

```mermaid
graph TD
    A[CLI / main] -->|load config| B[ConfigLoader]
    B -->|AppConfig(csv_path, window_size, initial_step)| A
    A -->|csv_path| C[DataHandler]
    C -->|load CSV → DataFrame| C
    A -->|construct| D[TradingEngine]
    A -->|construct| E[Chart]
    A -->|construct| F[Viewer]

    F -->|calls get_visible_window(current_step, window_size)| C
    C -->|returns visible_df, start_index| F
    F -->|calls get_price(step)| C
    C -->|returns price| F
    F -->|calls get_status(price)| D
    D -->|returns status dict| F
    F -->|calls chart.render(visible_df, current_step, start, status)| E
    E -->|draws| G[Matplotlib UI]
    G -->|user key events| F
    F -->|key actions (open/close/step)| D & C & F
```

この図は実際のコード呼び出し順を反映しています。