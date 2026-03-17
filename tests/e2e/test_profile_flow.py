import json
import pytest

from src import handler as handler_mod
from tests.events import apigw_v1_event
from tests.factories import profile_body, profile_response, error_body, ok_body, unique_user_id

pytestmark = pytest.mark.e2e


def make_profile_event(method: str, user_id: str, body_obj=None):
    return apigw_v1_event(
        method,
        "/users/{id}/profile",
        path_params={"id": user_id},
        body_obj=body_obj,
    )


def assert_json_response(resp, status_code: int, expected_body: dict):
    assert resp["statusCode"] == status_code
    assert resp["headers"]["Content-Type"] == "application/json"
    assert json.loads(resp["body"]) == expected_body


def test_profile_flow_post_then_get(patch_handler_repo):
    user_id = unique_user_id()
    # 1. POST
    post_event = make_profile_event("POST", user_id, profile_body(name="alice"))
    assert_json_response(handler_mod.handler(post_event, None), 200, ok_body())

    # 2. GET
    get_event = make_profile_event("GET", user_id)
    assert_json_response(handler_mod.handler(get_event, None), 200, profile_response(user_id, "alice"))


def test_profile_flow_get_missing_returns_404(patch_handler_repo):
    event = apigw_v1_event(
        "GET",
        "/users/{id}/profile",
        path_params={"id": "999"},
    )
    assert_json_response(handler_mod.handler(event, None), 404, error_body("NOT_FOUND", "not found"))


def test_profile_flow_post_invalid_name_returns_400(patch_handler_repo):
    event = apigw_v1_event(
        "POST",
        "/users/{id}/profile",
        path_params={"id": "123"},
        body_obj=profile_body(name=""),
    )
    assert_json_response(handler_mod.handler(event, None), 400, error_body("BAD_REQUEST", "bad request"))
