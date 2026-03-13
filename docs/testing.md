# Testing Guide

## First steps
- 普段の確認は `python -m pytest tests/unit`
- 永続化の確認は `python -m pytest -m integration tests/integration`
- 主要フローの確認は `python -m pytest -m e2e tests/e2e`
- 収集対象の確認は `python -m pytest --collect-only`
- 遅いテストは CI の `--durations=10` ログを見る

## Reading order
1. CI workflow overview
2. Test pyramid policy
3. E2E の定義
4. DynamoDB integration test の実行方法
5. Test performance baseline

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

## プラグイン
### pytest-mock
* 何を解決：unittest.mock を pytest の fixture として扱いやすくする（mocker）
* よく使う：mocker.patch(...) / mocker.patch.object(...) / mocker.patch.dict(...)
* 注意：差し替える先は「使っている側のモジュール名」（import先）

### pytest-cov
* 何を解決：coverage.py とpytestをつないで、テスト実行時にカバレッジを出す
* よく使う：--cov=src --cov-report=term-missing --cov-report=xml
* 注意：unitだけ測る/全体測るは運用方針次第（今は unit を指標、integration は別）

### pytest-xdist
* 何を解決：テストを並列実行して短縮する（-n 2 など）
* よく使う：-n 2、必要なら --dist=loadscope
* 注意：共有状態（環境変数/グローバル/固定キー）で壊れやすい → 隔離が正義

## テストチェクリスト
* 意図が読める名前：テスト名は「条件→結果」が分かる（例：test_get_profile_404_when_missing）
* Arrange/Act/Assertが分離：セットアップが長すぎない、assertが目立つ
* unit/integrationの境界が適切：I/Oはintegration、ロジックはunit
* モックの当て先が正しい：importされている側（使っているモジュール）をpatchしている
* モックしすぎてない：境界だけモックして、内部ロジックまでモックしない
* テストが独立：順序依存がない（固定ID/固定テーブル名/グローバル汚染がない）
* 失敗時に原因が分かる：assertが具体的（message/codeなど）で、雑な assert True がない
* パラメタライズが適切：似たテストは parametrize、ただし読みやすさ優先
* 例外・エラーの形式が統一：APIのエラーレスポンス（code/message）を固定している
* 実行時間意識：unitは速い、遅いものはintegrationに寄せ本数を制限

## DynamoDB integration test の実行方法

### 1. moto で実行する（デフォルト）

通常は追加設定なしで moto を使う。

```bash
python -m pytest -q -m integration tests/integration
```

### 2. DynamoDB Local で実行する

#### 2-1. Docker で起動

```bash
docker run --rm -p 8000:8000 amazon/dynamodb-local
```

別ターミナルで実行する。

#### 2-2. 環境変数を設定して pytest 実行（PowerShell）

```powershell
$env:AWS_REGION="ap-northeast-1"
$env:AWS_ACCESS_KEY_ID="dummy"
$env:AWS_SECRET_ACCESS_KEY="dummy"
$env:DYNAMODB_ENDPOINT_URL="http://localhost:8000"
python -m pytest -q -m integration tests/integration
```

### 3. 使い分け

* **moto**：普段の軽い確認用
* **DynamoDB Local**：motoとの差分が気になる時、本番寄りに確認したい時

### 4. よくあるエラー

* `Connection refused`
  → DynamoDB Local が起動していない、またはポート 8000 が使えない

* `Unable to locate credentials`
  → `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` にダミー値を入れる

* `ResourceInUseException`
  → テーブル名が重複している可能性がある。テストごとにランダム名を使う

## DynamoDB Local の運用方針

- CI の integration テストは、現時点では **moto** を使う。
- **DynamoDB Local** は、moto との差分確認や本番寄りの検証をしたいときに **ローカルで手動実行**する。
- 理由は、CI に Local を入れるとセットアップが重くなり、学習段階では保守コストが上がるため。
- まずは **ローカルで安定運用**し、必要性が明確になったら CI への導入を検討する。

## DynamoDB Local の典型トラブル

### 1. Connection refused
- 原因：DynamoDB Local が起動していない、またはポート `8000` が使えない
- 対処：Docker コンテナ起動を確認し、`http://localhost:8000` を使っているか確認する

### 2. Unable to locate credentials
- 原因：boto3 が認証情報を要求している
- 対処：PowerShell で `AWS_ACCESS_KEY_ID=dummy` と `AWS_SECRET_ACCESS_KEY=dummy` を設定する

### 3. ResourceInUseException
- 原因：同じテーブル名で既に作成済み
- 対処：テストごとにランダムなテーブル名を使う。不要なテーブルは削除する

### 4. ResourceNotFoundException
- 原因：テーブル作成前にアクセスしている、またはテーブル名が違う
- 対処：fixture の作成順序と `TableName` を確認する

### 5. Region mismatch / endpoint mismatch
- 原因：`AWS_REGION` や `DYNAMODB_ENDPOINT_URL` の設定が期待と違う
- 対処：PowerShell の環境変数一覧を確認してから pytest を実行する

## 日常実行コマンド
- moto: `.\scripts\run_integration_moto.ps1`
- local: `.\scripts\run_integration_local.ps1`

## E2E の定義

このリポジトリでは、E2E は「API Gateway に近いイベントを使って handler を呼び、
永続化を伴う主要フローを確認するテスト」とする。

## E2E の運用

- E2E テストは通常の push / pull_request では実行しない
- 必要なときに GitHub Actions の手動実行 (`workflow_dispatch`) で回す
- 理由：E2E は本数を最小に保ち、通常CIの速度を落とさないため

## E2E 安定化ルール

- E2E では固定IDを避け、必要に応じてユニークなテストデータを使う
- E2E は共有状態に依存させず、1回目と2回目で同じ結果になることを重視する

## Test performance baseline

- unit: 0.37s
- integration: 0.95s
- e2e: 0.94s

### Notes
- unit は主にロジック検証で、並列実行を前提にする
- integration は DynamoDB の setup コストが支配的になりやすい
- e2e は本数を最小に保ち、手動実行を基本とする

## Performance analysis notes

- unit は 0.37s で十分速い
- integration / e2e は 1s 前後で、主な遅さは test body ではなく setup にある
- setup の主因候補は DynamoDB resource の初期化とテーブル作成/削除
- 現時点では、速度よりもテスト隔離（function scope）を優先する

## Slow test の確認

- integration / e2e の遅いテストは GitHub Actions のログで `--durations=10` を確認する
- 遅さの主因が `setup` なら fixture / テーブル作成 / resource 初期化を疑う

## xdist evaluation

- unit (serial): 0.36
- unit (-n 2): 1.42
- unit (-n 2 --dist=loadscope): 1.62

### Decision
- 現在のテスト数では serial が適している
- 今後 unit テストが増えたら再評価する
- 現在の規模では `-n 2` の効果は限定的だが、将来の unit テスト増加を見越して CI では維持する

## Test collection notes

- 収集対象の確認には `pytest --collect-only` を使う
- 収集が遅いときは、`conftest.py` の配置と import の重さを疑う
- unit では root の `tests/conftest.py` に重い依存を置かない

## DynamoDB Local in CI

- 現時点では、DynamoDB Local は CI に導入しない
- 理由は、moto による integration が既にあり、Local はローカルで確認できるため
- CI に Local を導入するのは、moto では再現できない差分が継続的に問題になった場合に検討する

## E2E rerun check

- E2E を追加・変更したら、連続で2回実行して再現性を確認する
- ローカルで `DYNAMODB_ENDPOINT_URL` が残っていないか確認してから実行する

## Test pyramid policy

- unit テストを中心にし、ロジック・バリデーション・エラーハンドリングを素早く確認する
- integration テストは DynamoDB との永続化確認など、I/O 境界に限定する
- e2e テストは主要フローのみを最小本数で持ち、通常CIではなく手動実行を基本とする
- 新しいテストを追加する時は、まず unit で表現できないかを先に検討する
- 現在の構成では、unit を厚くして integration / e2e を絞る方針が適している

## CI workflow overview

| test type | trigger | purpose |
|---|---|---|
| unit | push / pull_request | ロジックとバリデーションを高速に確認する |
| integration | main push / manual | DynamoDB との永続化や I/O 境界を確認する |
| e2e | manual | 主要フローを end-to-end で確認する |

### Notes
- 通常の開発では unit を主なフィードバックとする
- integration / e2e は本数を絞り、必要な時に実行する

## What to bring back to work

### Topic
unit / integration の分離を進める

### First small step
- 既存のテストを1本選び、DBや外部I/Oに触るかを確認する
- 触らないものは unit に寄せ、mock で差し替える
- DBに触るものは integration に残す
- まずは 1テストだけ移動・整理して、差分を小さくする

## What I can do now

- pytest で unit / integration / e2e を分けて設計・運用できる
- mocker / caplog / capsys / tmp_path を用途別に使い分けられる
- CI で unit / integration / e2e の実行条件を分け、coverage や durations を運用できる
- DynamoDB (pk/sk) と API Gateway Proxy を前提に、handler/service/repo のテスト戦略を組める
- docs と scripts を含めて、再実行しやすいテスト運用を整えられる

## Local DynamoDB note
- 条件付き更新（ConditionExpression）は Local でも通ることを確認した
- `localcheck` マーカーは、DynamoDB Local でも確認したい integration テストに付ける

## moto / DynamoDB Local の使い分け

- 通常の integration テストは moto を使って高速に確認する
- DynamoDB 固有の挙動を強く意識したいテストは Local でも確認する
- 現時点では、条件付き更新（ConditionExpression / UpdateItem）を Local 確認対象とする