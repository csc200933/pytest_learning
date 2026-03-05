import json
import logging
import pytest

from src import handler as handler_mod
from tests.factories import profile_body
from tests.events import apigw_v1_event
from tests.factories import error_body, ok_body

class DummyRepo:
    def __init__(self, table_name: str):
        self.table_name = table_name

def call_profile_handler(mocker, *, method, user_id="123", body=None, fetch=None, upsert=None, raw_body=None):
    mocker.patch.object(handler_mod, "DynamoRepo", DummyRepo)

    if fetch is not None:
        mocker.patch.object(handler_mod.service, "fetch_profile", side_effect=fetch)
    if upsert is not None:
        mocker.patch.object(handler_mod.service, "upsert_profile", side_effect=upsert)

    event = apigw_v1_event(
        method,
        "/users/{id}/profile",
        path_params={"id": user_id},
        body_obj=body,
    )

    if raw_body is not None:
        event["body"] = raw_body

    return handler_mod.handler(event, None)

class TestPostProfile:
    def test_post_profile_200(self, mocker):
        called = {}

        def fake_upsert(repo, user_id, name):
            assert isinstance(repo, DummyRepo)
            called["user_id"] = user_id
            called["name"] = name

        resp = call_profile_handler(
            mocker,
            method="POST",
            user_id="123",
            body=profile_body(name="alice"),
            upsert=fake_upsert,
        )

        assert resp["statusCode"] == 200
        assert json.loads(resp["body"]) == ok_body()
        assert called == {"user_id": "123", "name": "alice"}

    @pytest.mark.parametrize(
        "user_id, body, raw_body, case",
        [
            ("", profile_body(name="alice"), None, "missing user_id"),
            ("123", {}, None, "missing name"),
            ("123", {"name": ""}, None, "empty name"),
            ("123", None, "{invalid json", "invalid json"),
        ],
        ids=lambda x: x if isinstance(x, str) else None,  # case名が表示される
    )
    def test_post_profile_400_bad_request(self, mocker, user_id, body, raw_body, case):

        resp = call_profile_handler(
            mocker,
            method="POST",
            user_id=user_id,
            body=body,
            raw_body=raw_body,
            upsert=lambda *args, **kwargs: None,  # 呼ばれても害はない
        )

        assert resp["statusCode"] == 400
        assert json.loads(resp["body"]) == error_body("BAD_REQUEST", "bad request")


    @pytest.mark.parametrize(
        "name",
        ["", "a" * 51],
        ids=["empty", "too_long"],
    )
    def test_post_profile_400_when_name_invalid_length(self, mocker, name):
        resp = call_profile_handler(
            mocker,
            method="POST",
            user_id="123",
            body=profile_body(name=name),
            upsert=lambda *args, **kwargs: None,
        )
        assert resp["statusCode"] == 400
        assert json.loads(resp["body"]) == error_body("BAD_REQUEST", "bad request")


    @pytest.mark.parametrize(
        "name",
        ["a", "a" * 50],
        ids=["min_ok", "max_ok"],
    )
    def test_post_profile_200_when_name_valid_length(self, mocker, name):
        resp = call_profile_handler(
            mocker,
            method="POST",
            user_id="123",
            body=profile_body(name=name),
            upsert=lambda *args, **kwargs: None,
        )
        assert resp["statusCode"] == 200
        assert json.loads(resp["body"]) == ok_body()

class TestGetProfile:
    def test_get_profile_200(self, mocker):
        def fake_fetch(repo, user_id):
            assert isinstance(repo, DummyRepo)
            assert user_id == "123"
            return {"pk": "USER#123", "sk": "PROFILE", "name": "alice"}

        resp = call_profile_handler(mocker, method="GET", user_id="123", fetch=fake_fetch)

        assert resp["statusCode"] == 200
        assert json.loads(resp["body"])["name"] == "alice"

    def test_get_profile_404(self, mocker):
        resp = call_profile_handler(
            mocker,
            method="GET",
            user_id="nope",
            fetch=lambda repo, user_id: None,
        )

        assert resp["statusCode"] == 404
        assert json.loads(resp["body"]) == error_body("NOT_FOUND", "not found")

    def test_unhandled_exception_logs_and_returns_500(self, mocker, caplog):
        # env / DynamoRepo差し替えなど：あなたの call_profile_handler に任せる想定
        def boom(*args, **kwargs):
            raise RuntimeError("boom")

        caplog.set_level(logging.ERROR)

        resp = call_profile_handler(
            mocker,
            method="GET",
            user_id="123",
            fetch=boom,   # fetch_profile が落ちる
        )

        assert resp["statusCode"] == 500
        assert json.loads(resp["body"]) == error_body("INTERNAL_ERROR", "internal server error")

        # ログに例外が残っていること（メッセージでも例外文字列でもOK）
        assert "Unhandled error" in caplog.text
        assert "boom" in caplog.text

class TestMethodNotAllowed:
    @pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
    def test_method_not_allowed(self, mocker, method):
        resp = call_profile_handler(
            mocker,
            method=method,
            user_id="123",
        )

        assert resp["statusCode"] == 405
        assert json.loads(resp["body"]) == error_body("METHOD_NOT_ALLOWED", "method not allowed")

