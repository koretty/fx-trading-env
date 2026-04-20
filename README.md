# Fx-Trading-Env

> Gymnasium互換のFX取引シミュレーション環境。学習向けのヘッドレス実行と、デバッグ用Viewerを分離したプロジェクトです。

---

## Overview

このリポジトリは USD/JPY の OHLC 時系列データを使って、強化学習エージェントが `reset` / `step` ベースで取引を進められる環境を提供します。
中核は `FxGymEnv` で、データ読み込み・取引ロジック・観測生成・報酬計算・可視化を責務分離しています。

### 実装済みの主な機能

- Gymnasium互換環境 `src/envs/fx_gym_env.py`
  - 4アクション: `hold(0)` / `long(1)` / `short(2)` / `close(3)`
  - 終了条件: データ末尾到達 または 証拠金維持率割れ（マージンコール）
  - 打ち切り条件: `max_episode_steps` 到達時に `truncated=True`
- `src/core/data_handler.py`
  - CSV列名を正規化（`<OPEN>` のような形式にも対応）
  - 読み込み時に NumPy 配列へ変換し、ステップループを高速化
  - 範囲外stepアクセス時に例外を送出し、lookaheadを防止
- `src/core/engine.py`
  - スプレッド考慮の約定（ask/bid）
  - `balance` / `equity` / `unrealized_pnl` / `win_rate` / `maintenance_margin_ratio` を計算
- プラグイン構造
  - 観測: `OHLCWindowFeature`
  - 報酬: `PnLDeltaReward`
- `src/visualization/viewer.py`
  - 環境本体とは独立したデバッグクライアント
  - キー入力による手動ステップと、Spaceキーによる自動再生（1秒間隔）

---

## Requirements

- Python 3.10+
- 必須ライブラリ
  - gymnasium
  - numpy
  - pandas
  - matplotlib
- 任意ライブラリ
  - pyyaml（YAML設定ファイルを使う場合のみ）

---

## Installation

```bash
git clone <your-repo-url>
cd fx-trading-env
pip install gymnasium numpy pandas matplotlib pyyaml
```

---

## Quick Start

```bash
# デバッグViewer起動
python src/main.py --mode viewer

# ヘッドレス実行（holdのみで200ステップ）
python src/main.py --mode headless --steps 200

# Gymnasium API互換チェック
python src/check.py
```

設定ファイルを使う例:

```bash
python src/main.py --config config.yaml --mode viewer
python src/check.py --config config.json --max-episode-steps 500
```

---

## CLI Options

### `src/main.py`

- `--config`: 設定ファイル（`.json` / `.yaml` / `.yml`）
- `--csv`: OHLC CSVのパス（設定ファイルより優先）
- `--window-size`: 観測窓サイズ
- `--initial-step`: 起動時ステップ（`env.reset(options={"start_step": ...})`）
- `--mode`: `viewer` または `headless`
- `--steps`: `headless` モード時のステップ数

### `src/check.py`

- `--config`
- `--csv`
- `--window-size`
- `--max-episode-steps`: truncation動作を含めたチェックに利用可能

---

## Action / Viewer Key Map

環境アクション:

- `0`: hold
- `1`: long（既存ポジションがあれば一度closeしてから建玉）
- `2`: short（既存ポジションがあれば一度closeしてから建玉）
- `3`: close

Viewerキー:

- `Right`: holdして1ステップ進む
- `A`: longして1ステップ進む
- `Z`: shortして1ステップ進む
- `X`: closeして1ステップ進む
- `Space`: hold自動再生のON/OFF（1秒間隔）
- `Home`: reset

---

## Configuration

`ConfigLoader` が読み込む設定キー:

- `csv_path` (string)
- `window_size` (int, > 0)
- `initial_step` (int, >= 0)

YAML例:

```yaml
csv_path: src/USDJPY_M5_202411130555_202512311810.csv
window_size: 120
initial_step: 120
```

JSON例:

```json
{
  "csv_path": "src/USDJPY_M5_202411130555_202512311810.csv",
  "window_size": 120,
  "initial_step": 120
}
```

---

## `info` に含まれる主な指標

`reset` / `step` が返す `info` には、次のような指標が含まれます。

- `current_step`, `action`, `price`
- `position_side`, `entry_mid_price`, `entry_price`
- `balance`, `unrealized_pnl`, `maintenance_margin_ratio`, `is_margin_call`
- `equity`, `episode_total_reward`
- `episode_peak_equity`, `episode_max_drawdown`, `episode_max_drawdown_pct`
- `closed_trades`, `winning_trades`, `losing_trades`, `win_rate`, `total_realized_pnl`

---

## Project Structure

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
│   ├── check.py
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

---

## License

MIT License
