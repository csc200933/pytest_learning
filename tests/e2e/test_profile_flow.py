import json
import pytest

from src import handler as handler_mod
from tests.events import apigw_v1_event
from src.repo_dynamo import DynamoRepo
from tests.factories import profile_body, profile_response, ok_body

pytestmark = pytest.mark.e2e


def test_profile_flow_post_then_get(mocker, dynamodb_resource, items_table):
    # handler が new する DynamoRepo を、同じ dynamodb_resource を使うものに差し替える
    def repo_factory(table_name: str):
        return DynamoRepo(table_name=table_name, dynamodb_resource=dynamodb_resource)

    mocker.patch.object(handler_mod, "DynamoRepo", side_effect=repo_factory)

    import os
    mocker.patch.dict(os.environ, {"TABLE_NAME": items_table.name}, clear=False)

    # 1. POST
    post_event = apigw_v1_event(
        "POST",
        "/users/{id}/profile",
        path_params={"id": "123"},
        body_obj=profile_body(name="alice"),
    )
    post_resp = handler_mod.handler(post_event, None)

    assert post_resp["statusCode"] == 200
    assert json.loads(post_resp["body"]) == ok_body()

    # 2. GET
    get_event = apigw_v1_event(
        "GET",
        "/users/{id}/profile",
        path_params={"id": "123"},
    )
    get_resp = handler_mod.handler(get_event, None)

    assert get_resp["statusCode"] == 200
    assert json.loads(get_resp["body"]) == profile_response("123", "alice")