## This code base is assisted by ChatGPT

## Unit / Integration の境界（判断基準）

* **Unit**：DynamoDBや外部I/Oを呼ばず、`service` の分岐・バリデーション・レスポンス整形を検証する（repoはmockerで差し替える）。
* **Integration**：実際に DynamoDB に **書ける/読める**ことを保証したい最小フローだけ（Put/Get など “永続化の事実” が目的）。
* **原則**：同じ仕様は unit を優先。integration は “落ちると本番事故” になる箇所に限定して本数を増やさない。
* **速度**：unit は常時（PR/Push）実行、integration は main の push や手動実行に限定する。
* **失敗の切り分け**：unit が落ちたらロジック、integration が落ちたら依存（Dynamo/設定/権限/互換性）を疑う。
