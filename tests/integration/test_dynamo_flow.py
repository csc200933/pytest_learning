from src.repo_dynamo import DynamoRepo
from src import service

def test_upsert_and_fetch_profile_integration(dynamodb_resource, items_table):
    repo = DynamoRepo(items_table.name, dynamodb_resource=dynamodb_resource)

    service.upsert_profile(repo, "123", "alice")
    item = service.fetch_profile(repo, "123")

    assert item is not None
    assert item["pk"] == "USER#123"
    assert item["sk"] == "PROFILE"
    assert item["name"] == "alice"