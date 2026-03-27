# 問題点と改善提案

## 実施済みの改善
- 主従関係を修正: FxGymEnv を中核にし、Viewer は env.step(action) を呼ぶデバッグクライアント化。
- Gymnasium互換追加: src/envs/fx_gym_env.py を実装し、reset/step/action_space/observation_space を提供。
- 性能改善: DataHandler はロード時に NumPy 配列へ変換し、ステップ中は高速な配列アクセス。
- プラグイン機構追加: src/core/features.py と src/core/rewards.py を導入。
- ConfigLoader拡張: src/utils/config_loader.py で YAML / JSON 設定ファイル読み込みと CLI override を統合。
- ルックアヘッド防止: src/core/data_handler.py の get_ohlc_window(step, ...) で範囲外stepアクセス時に例外を送出し、未来参照を禁止。
- TradingEngine拡張: open_long/open_short/close にスプレッド考慮を導入し、uPnL/実現損益と証拠金維持率判定を追加。
- Feature/Reward整備: OHLCWindowFeature と PnLDeltaReward を強化し、Gym統合前でも単体ロジック検証しやすい形へ整理。

## 残課題（次の改善候補）

- 1) 取引コストモデルの追加拡張
  - 既存の spread に加え、commission/slippage を RewardFunction へ統合する。

- 2) 観測量の拡張
  - OHLC以外にテクニカル指標やボラティリティ特徴を FeatureExtractor へ追加する。

- 3) 早期終了条件の追加拡張
  - 既存の証拠金維持率割れ判定に加え、ドローダウン閾値を terminated 条件へ統合する。

- 4) 自動テストの強化
  - Envの reset/step 契約、Observation shape/dtype、Reward の境界条件をテスト化。

- 5) 設定スキーマの明文化
  - JSON/YAML で許可するキーと型を docs に明記し、設定ミスを減らす。

## 実装チェックリスト（現時点）
- [x] Gymnasium互換 env を追加
- [x] Feature/Reward プラグイン機構を追加
- [x] DataHandler を NumPy中心へ改修
- [x] Viewer を Env駆動デバッグ化
- [x] ConfigLoader を YAML / JSON 両対応へ拡張
- [x] get_ohlc_window に未来参照防止（例外送出）を実装
- [x] TradingEngine にスプレッド計算・uPnL・維持率割れ判定を実装
- [x] Observation/Reward のコアロジックを更新
- [ ] テストコード整備（次フェーズ）