import json
import pytest

from src import handler as handler_mod
from tests.events import apigw_v1_event
from tests.factories import profile_body, profile_response, error_body, ok_body, unique_user_id

pytestmark = pytest.mark.e2e


def test_profile_flow_post_then_get(patch_handler_repo):
    user_id = unique_user_id()
    # 1. POST
    post_event = apigw_v1_event(
        "POST",
        "/users/{id}/profile",
        path_params={"id": user_id},
        body_obj=profile_body(name="alice"),
    )
    post_resp = handler_mod.handler(post_event, None)

    assert post_resp["statusCode"] == 200
    assert post_resp["headers"]["Content-Type"] == "application/json"
    assert json.loads(post_resp["body"]) == ok_body()

    # 2. GET
    get_event = apigw_v1_event(
        "GET",
        "/users/{id}/profile",
        path_params={"id": user_id},
    )
    get_resp = handler_mod.handler(get_event, None)

    assert get_resp["statusCode"] == 200
    assert set(json.loads(get_resp["body"]).keys()) == set(profile_response(user_id, "alice").keys())    


def test_profile_flow_get_missing_returns_404(patch_handler_repo):
    event = apigw_v1_event(
        "GET",
        "/users/{id}/profile",
        path_params={"id": "999"},
    )
    resp = handler_mod.handler(event, None)

    assert resp["statusCode"] == 404
    assert resp["headers"]["Content-Type"] == "application/json"
    assert json.loads(resp["body"]) == error_body("NOT_FOUND", "not found")


def test_profile_flow_post_invalid_name_returns_400(patch_handler_repo):
    event = apigw_v1_event(
        "POST",
        "/users/{id}/profile",
        path_params={"id": "123"},
        body_obj=profile_body(name=""),
    )

    resp = handler_mod.handler(event, None)

    assert resp["statusCode"] == 400
    assert resp["headers"]["Content-Type"] == "application/json"
    assert json.loads(resp["body"]) == error_body("BAD_REQUEST", "bad request")
