$env:AWS_REGION="ap-northeast-1"
$env:AWS_ACCESS_KEY_ID="dummy"
$env:AWS_SECRET_ACCESS_KEY="dummy"
$env:DYNAMODB_ENDPOINT_URL="http://localhost:8000"

python -c "
import os, sys, boto3
from botocore.config import Config

client = boto3.client(
    'dynamodb',
    region_name=os.getenv('AWS_REGION', 'ap-northeast-1'),
    endpoint_url=os.getenv('DYNAMODB_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'dummy'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'dummy'),
    config=Config(
        connect_timeout=1,
        read_timeout=1,
        retries={'max_attempts': 0}
    )
)

client.list_tables()
print('DynamoDB Local is reachable')
"

if ($LASTEXITCODE -ne 0) {
    Write-Error "DynamoDB Local is not reachable via boto3"
    exit 1
}

python -m pytest -q -m integration tests/integration