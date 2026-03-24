# 問題点と改善提案

## 現状の観察
- 責務分離は概ね良好（`DataHandler`, `TradingEngine`, `Chart` に分かれている）。
- `Viewer` が複数の責務（合成・UI制御）を持つ。
- `ConfigLoader._resolve_csv_path` のベースパス決定がハードコーディング気味。
- `Chart` と `DataHandler` が `pandas.DataFrame` を直接やり取りしているため、描画テストがやや難しい。

## 改善提案（優先順）

- 1) `Controller` を外部注入に完全に切り替える
  - 理由: テスト性とカスタムキーバインドの容易化。
  - 変更点: `Viewer` のコンストラクタで `controller` を必須または明示的に提供させる。

- 2) 描画インターフェースの抽象化
  - 理由: `Chart.render()` に渡す型を DTO（例: Candle[]）にすることで、`pandas` 依存を描画層に閉じ込める。

- 3) 設定パス解決の改善
  - 理由: `parents[2]` の依存は配置変更で壊れる。
  - 変更点: 環境変数やプロジェクトルート検出ルールを採用する。

- 4) `TradingEngine` のイベントフック導入
  - 理由: 将来的な戦略プラグインやログ、UI 更新を容易にするため。

## 実装チェックリスト（小さなステップ）
- [ ] `Viewer` の `controller` を外部注入に移行
- [ ] `Chart` の入出力インターフェースを DTO に変更し、`pandas` は `DataHandler` 側でのみ扱う
- [ ] `ConfigLoader` のベースパス検出をリファクタ
- [ ] `TradingEngine` にイベントコールバックを追加

必要なら、これら改善のパッチを作成します。どれを優先しますか？