import pytest
from src.repo_dynamo import DynamoRepo
from src import service

pytestmark = pytest.mark.integration


def test_upsert_and_fetch_profile_integration(dynamodb_resource, items_table):
    repo = DynamoRepo(items_table.name, dynamodb_resource=dynamodb_resource)

    service.upsert_profile(repo, "123", "alice")
    item = service.fetch_profile(repo, "123")

    assert item is not None
    assert item["pk"] == "USER#123"
    assert item["sk"] == "PROFILE"
    assert item["name"] == "alice"


# This test is also a good candidate for DynamoDB Local verification.
@pytest.mark.localcheck
def test_update_item_conditionally(dynamodb_resource, items_table):
    repo = DynamoRepo(items_table.name, dynamodb_resource=dynamodb_resource)

    # 1) まず作る → 更新できる
    service.upsert_profile(repo, "123", "alice")
    service.update_profile_name_if_exists(repo, "123", "bob")

    item = service.fetch_profile(repo, "123")
    assert item["name"] == "bob"

    # 2) 存在しない → 条件付き失敗（あなたの方針に合わせてどっちでも）
    with pytest.raises(KeyError):
        service.update_profile_name_if_exists(repo, "999", "x")
