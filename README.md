# Fx-Trading-Env

> Gymnasium互換のFX取引シミュレーション環境を中心に、ヘッドレス実行とデバッグ可視化を分離した学習用プロジェクト。

---

## Overview

このプロジェクトは、USD/JPYのOHLC時系列データを使って、強化学習向けに取引環境を1ステップずつ進められるようにした実装です。中核は `FxGymEnv` で、`reset` / `step` / `action_space` / `observation_space` を備えたGymnasium互換APIとして構成されています。

設計上は、データ読み込み、売買ロジック、観測生成、報酬計算、可視化をモジュール分離しています。特に `DataHandler` でCSVを初期ロード時にNumPy化し、ステップループでのオーバーヘッドを抑えている点と、Viewerを環境本体から独立させている点が実装済みの特徴です。

### Features

* Gymnasium互換環境 `src/envs/fx_gym_env.py` を実装（4アクション: hold/long/short/close）
* `src/core/data_handler.py` でCSVを検証・正規化し、NumPy配列ベースで高速アクセス
* `src/core/features.py` と `src/core/rewards.py` による特徴量/報酬の差し替え可能な構造

---

## Demo

現時点ではREADME向けの静的デモ画像は未配置です。`--mode viewer` で起動すると、Matplotlib上でローソク足とポジション状態を確認できます。

---

## Quick Start

最短で動作確認するため、必要ライブラリを入れて `src/main.py` または `src/check.py` を実行します。

### Requirements

* 言語 / ランタイム: Python 3.10+
* 必要ライブラリ: gymnasium, numpy, pandas, matplotlib
* 任意ライブラリ: PyYAML（YAML設定ファイルを使う場合のみ）

### Installation

```bash
git clone <your-repo-url>
cd fx-trading-env

pip install gymnasium numpy pandas matplotlib pyyaml
```

### Run

```bash
# デバッグビューア起動
python src/main.py --mode viewer

# ヘッドレス実行（holdのみで100ステップ）
python src/main.py --mode headless --steps 100

# Gymnasium互換チェック
python src/check.py
```

---

## Usage

`viewer` モードではキー入力でアクションを送り、`headless` モードでは画面なしで環境を進められます。

### Example

```bash
# Viewer の操作キー
# right : holdして1ステップ進む
# a     : longして1ステップ進む
# z     : shortして1ステップ進む
# x     : closeして1ステップ進む
# home  : reset
```

### Configuration

```json
{
  "csv_path": "src/USDJPY_M5_202411130555_202512311810.csv",
  "window_size": 120,
  "initial_step": 120
}
```

CLIオプション（`--csv` / `--window-size` / `--initial-step`）は設定ファイルより優先されます。

---

## Tech Stack

実装済み機能で実際に使っている技術スタックです。

| Category       | Technology                     | Reason |
| :------------- | :----------------------------- | :----- |
| Runtime        | Python 3                       | Gymnasium環境とデータ処理を素早く実装できる |
| RL Interface   | Gymnasium                      | `reset/step`契約に沿った環境定義ができる |
| Data Handling  | pandas + NumPy                 | 読み込み時はpandas、ステップ時はNumPyで高速化 |
| Visualization  | Matplotlib                     | デバッグ用途のローソク足表示とキー操作連携 |

---

## Project Structure

主要ディレクトリは、責務ごとに分離した構成です。

```text
.
├── docs/
│   ├── architecture.md
│   ├── class_diagram.md
│   ├── data_flow.md
│   ├── dependency.md
│   └── recommendations.md
├── src/
│   ├── main.py                  # エントリポイント（viewer/headless）
│   ├── check.py                 # gymnasium.utils.env_checker 実行
│   ├── USDJPY_M5_*.csv          # サンプルOHLCデータ
│   ├── core/
│   │   ├── data_handler.py      # CSVロードと時系列ウィンドウ取得
│   │   ├── engine.py            # ポジション・損益・維持率判定
│   │   ├── features.py          # 観測ベクトル生成
│   │   └── rewards.py           # 報酬計算
│   ├── envs/
│   │   └── fx_gym_env.py        # Gymnasium互換環境
│   ├── utils/
│   │   └── config_loader.py     # YAML/JSON + CLI設定解決
│   └── visualization/
│       ├── chart.py             # チャート描画
│       ├── controller.py        # キー入力処理
│       └── viewer.py            # Envクライアント
└── README.md
```

---

## Roadmap

* [x] Gymnasium互換のFX環境（reset/step/action_space/observation_space）
* [x] DataHandlerのNumPy最適化と未来参照防止
* [x] Viewerを分離したデバッグ可視化
* [ ] 自動テスト整備（Env契約・境界ケース）
* [ ] 取引コストモデル拡張（commission/slippage）

---

## License

MIT License
