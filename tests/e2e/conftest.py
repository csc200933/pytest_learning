import os
import uuid
import pytest
import boto3
from moto import mock_aws

from src import handler as handler_mod
from src.repo_dynamo import DynamoRepo


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