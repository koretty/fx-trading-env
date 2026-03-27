# 問題点と改善提案

## 実施済みの改善
- 主従関係を修正: FxGymEnv を中核にし、Viewer は env.step(action) を呼ぶデバッグクライアント化。
- Gymnasium互換追加: src/envs/fx_gym_env.py を実装し、reset/step/action_space/observation_space を提供。
- 性能改善: DataHandler はロード時に NumPy 配列へ変換し、ステップ中は高速な配列アクセス。
- プラグイン機構追加: src/core/features.py と src/core/rewards.py を導入。
- ConfigLoader拡張: src/utils/config_loader.py で YAML / JSON 設定ファイル読み込みと CLI override を統合。
- ルックアヘッド防止: src/core/data_handler.py の get_ohlc_window(step, ...) で範囲外stepアクセス時に例外を送出し、未来参照を禁止。

## 残課題（次の改善候補）

- 1) 取引コストモデルの導入
  - spread, commission, slippage を RewardFunction に統合する。

- 2) 観測量の拡張
  - OHLC以外にテクニカル指標やボラティリティ特徴を FeatureExtractor へ追加する。

- 3) 早期終了条件の追加
  - ドローダウン閾値や証拠金不足を terminated 条件として扱う。

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
- [ ] テストコード整備（次フェーズ）