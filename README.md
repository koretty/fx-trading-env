# fx-trading-env

Gymnasium互換のFXトレーディング環境と、手動デバッグ用ビューアを備えたPythonプロジェクトです。

このリポジトリは、以下を分離して設計しています。

- 環境本体: `src/envs/fx_gym_env.py`
- 取引ロジック: `src/core/engine.py`
- 特徴量と報酬: `src/core/features.py`, `src/core/rewards.py`
- 可視化/UI: `src/visualization/`

## 主な機能

- Gymnasium API (`reset` / `step`) に準拠した環境
- OHLC CSVを読み込む高速データハンドラ（NumPy配列へ前処理）
- ポジション状態（LONG/SHORT/FLAT）とuPnL計算
- 特徴量抽出と報酬関数を差し替え可能な構成
- Matplotlibベースのデバッグビューア（キー操作で1ステップずつ検証）

## 前提環境

- Python 3.10+
- Windows / macOS / Linux（確認は主にWindows）



またはCSVを明示:

```bash
python src/main.py --csv src/USDJPY_M5_202411130555_202512311810.csv
```


## ディレクトリ構成

```text
.
├── docs/
│   ├── architecture.md
│   ├── class_diagram.md
│   ├── data_flow.md
│   ├── dependency.md
│   └── recommendations.md
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── data_handler.py
│   │   ├── engine.py
│   │   ├── features.py
│   │   └── rewards.py
│   ├── envs/
│   │   └── fx_gym_env.py
│   ├── utils/
│   │   └── config_loader.py
│   └── visualization/
│       ├── chart.py
│       ├── controller.py
│       └── viewer.py
└── README.md
```

## ライセンス

MIT
