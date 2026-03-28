# fx-trading-env

Gymnasium互換のFXトレーディング環境と、手動デバッグ用ビューアを備えたPythonプロジェクトです。

## 主な機能

- Gymnasium API  に準拠した環境
- FxGymEnvの`__init__`で Engine / Feature / Reward / DataHandler を組み立て可能（デフォルト構成）
- OHLC CSVを読み込む高速データハンドラ（NumPy配列へ前処理）
- `get_ohlc_window(step, ...)` で未来参照を禁止し、範囲外step時は例外を送出
- ポジション状態（LONG/SHORT/FLAT）、スプレッド考慮の約定、uPnL/実現損益計算
- 証拠金維持率の算出と維持率割れ（マージンコール）判定
- 特徴量抽出と報酬関数を差し替え可能な構成（Observation/Rewardロジックをコア層で分離）
- Matplotlibベースのデバッグビューア（キー操作で1ステップずつ検証）
- 設定ファイルの YAML / JSON 読み込み（CLI override対応）

## 前提環境

- Python 3.10+
- Windows 11

## ライセンス

MIT License