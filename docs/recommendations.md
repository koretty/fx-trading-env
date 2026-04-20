# 改善提案（2026-04-21時点）

`src` 配下のコード読解結果に基づく、現状整理と次アクションです。

## 現状で実装済みのポイント

- `FxGymEnv` は Gymnasium 契約（`reset/step/action_space/observation_space`）を満たす
- 終了条件は「データ末尾」または「マージンコール」
- `max_episode_steps` による `truncated` 判定に対応
- `DataHandler` はCSVを正規化し、NumPy配列へ変換して高速アクセス
- `TradingEngine` はスプレッド・実現/含み損益・維持率・勝率を管理
- `OHLCWindowFeature` / `PnLDeltaReward` による差し替え可能な構造
- ViewerはEnvクライアントとして分離され、手動/自動ステップが可能

## 優先度付きの改善候補

### 優先度 High

1. 自動テストの整備
   - 対象: `src/envs/fx_gym_env.py`, `src/core/data_handler.py`, `src/core/engine.py`
   - 目的: 仕様変更時のリグレッション防止
   - 最低限の観点:
     - `reset/step` の返却型・shape・dtype
     - 終了/打ち切り条件（末尾到達、マージンコール、max_episode_steps）
     - `get_ohlc_window` の境界動作（lookahead防止）

2. 設定バリデーションの強化
   - 対象: `src/utils/config_loader.py`
   - 目的: 実行前に設定ミスを明確化
   - 例: `csv_path` 存在確認、`window_size` とデータ長の整合、未知キーの検出

### 優先度 Medium

3. コストモデル拡張
   - 対象: `src/core/engine.py`, `src/core/rewards.py`
   - 目的: 学習環境を実運用に近づける
   - 例: commission、slippage、時間帯別スプレッド

4. 観測特徴量の拡張
   - 対象: `src/core/features.py`
   - 目的: 方策学習に有効な情報量を増やす
   - 例: リターン系列、ボラティリティ、移動平均乖離

5. エピソード結果の永続化
   - 対象: `src/main.py`（headless）
   - 目的: 実験比較を容易にする
   - 例: 1エピソードごとのメトリクスをCSV/JSONLへ保存

### 優先度 Low

6. Viewerの操作性改善
   - 対象: `src/visualization/viewer.py`, `src/visualization/chart.py`
   - 例: 再生速度切替、表示項目ON/OFF、スクリーンショット保存

## 推奨する次の実装順

1. テスト基盤を追加（pytest）
2. ConfigLoaderの入力検証を強化
3. コストモデルと報酬の拡張
4. 特徴量拡張と学習実験ログ整備