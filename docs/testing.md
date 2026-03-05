# pytest 調査コマンド集

> 目的：テストが落ちた/遅い/原因不明のときに、最短で切り分ける

## 基本

* 全テスト（通常）：`python -m pytest -q`
* unitのみ（普段）：`python -m pytest -q -m "not integration"`
* integrationのみ：`python -m pytest -q -m integration`

## 絞り込み

* 名前で絞る（部分一致）：`python -m pytest -q -k "profile and not 404"`
* マーカーで絞る：`python -m pytest -q -m "integration"`
* ファイル/ディレクトリ指定：`python -m pytest -q tests/unit/test_handler.py`

## 失敗の切り分け

* 最初の失敗で停止：`python -m pytest -q -x`
* 失敗数の上限：`python -m pytest -q --maxfail=1`
* 前回失敗したものだけ：`python -m pytest -q --lf`
* 失敗したものを先に：`python -m pytest -q --ff`
* 失敗の詳細表示：`python -m pytest -vv`

## 収集（discover）の確認

* 何が拾われているか：`python -m pytest --collect-only -q`
* マーカー適用後の収集確認：`python -m pytest --collect-only -q -m "not integration"`

## デバッグ（必要なときだけ）

* print を表示：`python -m pytest -q -s`
* ログ/出力を見ながら：`python -m pytest -vv -s`
* 実行時間上位：`python -m pytest -q --durations=10`

## 並列（unitのみ推奨）

* 並列（2ワーカー）：`python -m pytest -q -n 2 -m "not integration"`


## 並列で壊れないための3ルール
* テストは グローバル状態を書き換えない（環境変数・時刻・モジュール変数は fixture/patch で隔離）
* テストデータは テストごとに固有（idやテーブル名はuuid等で衝突回避）
* 外部I/Oを含むものは integrationに寄せて本数を絞る（並列対象は基本unit）