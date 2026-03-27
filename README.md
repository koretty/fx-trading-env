# fx-trading-env

Gymnasium互換のFXトレーディング環境と、手動デバッグ用ビューアを備えたPythonプロジェクトです。

## 主な機能

- Gymnasium API  に準拠した環境
- OHLC CSVを読み込む高速データハンドラ（NumPy配列へ前処理）
- `get_ohlc_window(step, ...)` で未来参照を禁止し、範囲外step時は例外を送出
- ポジション状態（LONG/SHORT/FLAT）とuPnL計算
- 特徴量抽出と報酬関数を差し替え可能な構成
- Matplotlibベースのデバッグビューア（キー操作で1ステップずつ検証）
- 設定ファイルの YAML / JSON 読み込み（CLI override対応）

## 前提環境

- Python 3.10+
- Windows 11

## ライセンス

MIT License