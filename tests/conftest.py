# tests/conftest.py
import os
import uuid
import pytest
import boto3
from moto import mock_aws

@pytest.fixture(scope="session")
def aws_region() -> str:
    return os.getenv("AWS_REGION", "ap-northeast-1")

@pytest.fixture
def table_name() -> str:
    return f"test_items_{uuid.uuid4().hex}"

@pytest.fixture
def dynamodb_resource(aws_region: str):
    with mock_aws():
        yield boto3.resource("dynamodb", region_name=aws_region)

@pytest.fixture
def items_table(dynamodb_resource, table_name: str):
    table = dynamodb_resource.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    yield table
    table.delete()