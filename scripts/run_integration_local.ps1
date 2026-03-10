$env:AWS_REGION="ap-northeast-1"
$env:AWS_ACCESS_KEY_ID="dummy"
$env:AWS_SECRET_ACCESS_KEY="dummy"
$env:DYNAMODB_ENDPOINT_URL="http://localhost:8000"

python -m pytest -q -m integration tests/integration