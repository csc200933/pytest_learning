import os
import json
import pytest

from src import handler as handler_mod
from tests.events import apigw_v1_event

class DummyRepo:
    def __init__(self, table_name: str):
        self.table_name = table_name

def test_handler_returns_200(monkeypatch):
    monkeypatch.setenv("TABLE_NAME", "dummy-table")
    monkeypatch.setattr(handler_mod, "DynamoRepo", DummyRepo)

    called = {}
    def fake_upsert_profile(repo, user_id, name):
        called["user_id"] = user_id
        called["name"] = name
        assert isinstance(repo, DummyRepo)

    monkeypatch.setattr(handler_mod.service, "upsert_profile", fake_upsert_profile)

    event = apigw_v1_event(
        "POST",
        "/users/{id}/profile",
        path_params={"id": "123"},
        body_obj={"name": "alice"},
    )

    resp = handler_mod.handler(event, context=None)

    assert resp["statusCode"] == 200
    assert json.loads(resp["body"]) == {"ok": True}
    assert called == {"user_id": "123", "name": "alice"}

def test_handler_missing_table_env(monkeypatch):
    monkeypatch.delenv("TABLE_NAME", raising=False)
    event = apigw_v1_event(
        "POST",
        "/users/{id}/profile",
        path_params={"id": "123"},
        body_obj={"name": "a"},
    )
    with pytest.raises(KeyError):
        handler_mod.handler(event, context=None)