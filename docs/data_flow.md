# Data Flow

データの流れ（入力 → 学習ループ → 出力）を示します。

- 入力: CSV（OHLC）
- 前処理: DataHandler.load() が CSV を読み込み、NumPy配列へ正規化
- 実行主体: RLエージェントが env.step(action) を呼ぶ
- 観測生成: FeatureExtractor が NumPy Observation を生成
- 報酬計算: RewardFunction が報酬を返す
- 可視化: Viewer は任意。Envの状態を読むデバッグクライアント

```mermaid
graph TD
    A[CLI / main] -->|load config| B[ConfigLoader]
    B -->|AppConfig(csv_path, window_size, initial_step)| A
    A -->|csv_path| C[DataHandler]
    C -->|load CSV once| C
    C -->|build NumPy arrays| C

    A -->|construct| D[FxGymEnv]
    D -->|uses| E[FeatureExtractor]
    D -->|uses| F[RewardFunction]
    D -->|uses| G[TradingEngine]

    H[RL Agent] -->|action| D
    D -->|step(action)| D
    D -->|observation: np.ndarray(Box)| H
    D -->|reward, terminated, truncated, info| H

    I[Viewer (optional)] -->|calls reset/step for debug| D
    I -->|get_debug_frame| D
    I -->|render| J[Chart]
    J -->|draw| K[Matplotlib UI]
```

実運用の主経路は RL Agent ↔ FxGymEnv です。Viewer経路は補助的なデバッグ用途です。