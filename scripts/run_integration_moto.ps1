Remove-Item Env:DYNAMODB_ENDPOINT_URL -ErrorAction SilentlyContinue
$env:AWS_REGION="ap-northeast-1"

python -m pytest -q -m integration tests/integration