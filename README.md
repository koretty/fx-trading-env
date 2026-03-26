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

## セットアップ

```bash
git clone <this-repository-url>
cd fx-trading-env

# 仮想環境は任意（例: conda / venv）
pip install numpy pandas gymnasium matplotlib
```

## 実行方法

### 1. Viewerモード（デフォルト）

```bash
python src/main.py
```

またはCSVを明示:

```bash
python src/main.py --csv src/USDJPY_M5_202411130555_202512311810.csv
```

### 2. Headlessモード（スモーク実行）

```bash
python src/main.py --mode headless --steps 200
```

実行後に `step` と `total_reward` を標準出力へ表示します。

## CLIオプション

```text
--config <path>        JSON設定ファイル
--csv <path>           OHLC CSVファイル
--window-size <int>    観測ウィンドウサイズ
--initial-step <int>   初期ステップ
--mode <viewer|headless>
--steps <int>          headless時の最大ステップ数
```

## 設定ファイル（任意）

`--config` でJSONを渡せます。CLI引数が優先されます。

```json
{
	"csv_path": "src/USDJPY_M5_202411130555_202512311810.csv",
	"window_size": 120,
	"initial_step": 120
}
```

## Viewerキー操作

- `Right`: 1ステップ進める（HOLD）
- `A`: LONGを建てる
- `Z`: SHORTを建てる
- `X`: ポジションをクローズ
- `Home`: リセット

## データ要件（CSV）

CSVには以下カラムが必要です（大文字小文字や`<>`は正規化されます）。

- `date`
- `time`
- `open`
- `high`
- `low`
- `close`

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