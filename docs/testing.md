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