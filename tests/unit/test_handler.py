import json
import logging
import pytest

from src import handler as handler_mod
from tests.events import apigw_v1_event

class DummyRepo:
    def __init__(self, table_name: str):
        self.table_name = table_name

def call_profile_handler(mocker, *, method, user_id="123", body=None, fetch=None, upsert=None, raw_body=None):
    import os
    mocker.patch.dict(os.environ, {"TABLE_NAME": "dummy-table"}, clear=False)

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
            body={"name": "alice"},
            upsert=fake_upsert,
        )

        assert resp["statusCode"] == 200
        assert json.loads(resp["body"]) == {"ok": True}
        assert called == {"user_id": "123", "name": "alice"}

    def test_post_profile_400_invalid_json(self, mocker):

        resp = call_profile_handler(
            mocker,
            method="POST",
            user_id="123",
            raw_body='{"name": "alice"',
            upsert=lambda repo, user_id, name: None
        )

        assert resp["statusCode"] == 400
        assert json.loads(resp["body"]) == {"message": "bad request"}

    def test_post_profile_400_missing_name(self, mocker):

        resp = call_profile_handler(
            mocker,
            method="POST",
            user_id="123",
            body={"user_id": "123"},
            upsert=lambda repo, user_id, name: None
        )

        assert resp["statusCode"] == 400
        assert json.loads(resp["body"]) == {"message": "bad request"}


    def test_post_profile_400_missing_user_id(self, mocker):

        resp = call_profile_handler(
            mocker,
            method="POST",
            user_id="",
            body={"name": "alice"},
            upsert=lambda repo, user_id, name: None
        )

        assert resp["statusCode"] == 400
        assert json.loads(resp["body"]) == {"message": "bad request"}


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
        assert json.loads(resp["body"]) == {"message": "not found"}

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
        assert json.loads(resp["body"]) == {"message": "internal server error"}

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
        assert json.loads(resp["body"]) == {"message": "method not allowed"}

