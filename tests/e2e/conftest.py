import os
import uuid
import pytest
import boto3
from moto import mock_aws

from src import handler as handler_mod
from src.repo_dynamo import DynamoRepo

@pytest.fixture(scope="session")
def aws_region() -> str:
    return os.getenv("AWS_REGION", "ap-northeast-1")


@pytest.fixture(scope="session")
def dynamodb_endpoint_url() -> str | None:
    return os.getenv("DYNAMODB_ENDPOINT_URL")


@pytest.fixture
def table_name() -> str:
    return f"test_items_{uuid.uuid4().hex}"


@pytest.fixture
def dynamodb_resource(aws_region: str, dynamodb_endpoint_url: str | None):
    if dynamodb_endpoint_url:
        yield boto3.resource(
            "dynamodb",
            region_name=aws_region,
            endpoint_url=dynamodb_endpoint_url,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "dummy"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "dummy"),
        )
    else:
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


@pytest.fixture
def patch_handler_repo(mocker, dynamodb_resource, items_table):
    def repo_factory(table_name: str):
        return DynamoRepo(table_name=table_name, dynamodb_resource=dynamodb_resource)

    mocker.patch.object(handler_mod, "DynamoRepo", side_effect=repo_factory)
    mocker.patch.dict(os.environ, {"TABLE_NAME": items_table.name}, clear=False)

    return {
        "table_name": items_table.name,
        "dynamodb_resource": dynamodb_resource,
    }