# tests/unit/test_service.py
import pytest
import re
from dataclasses import dataclass

from src import service

@dataclass
class FakeRepo:
    stored: dict  # key: (pk, sk)

    def put(self, pk: str, sk: str, attrs: dict) -> None:
        self.stored[(pk, sk)] = {"pk": pk, "sk": sk, **attrs}

    def get(self, pk: str, sk: str):
        return self.stored.get((pk, sk))

def test_upsert_profile_happy_path():
    repo = FakeRepo(stored={})
    service.upsert_profile(repo, "123", "alice")

    item = repo.get("USER#123", "PROFILE")
    assert item["name"] == "alice"

def test_upsert_profile_requires_user_id():
    repo = FakeRepo(stored={})
    with pytest.raises(ValueError, match=re.escape("user_id required")):
        service.upsert_profile(repo, "", "alice")

def test_upsert_profile_requires_name():
    repo = FakeRepo(stored={})
    with pytest.raises(ValueError, match=re.escape("name required")):
        service.upsert_profile(repo, "123", "")

def test_fetch_profile_requires_user_id():
    repo = FakeRepo(stored={})
    with pytest.raises(ValueError, match=re.escape("user_id required")):
        service.fetch_profile(repo, "")