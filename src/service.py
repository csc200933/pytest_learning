# src/service.py
from __future__ import annotations
from typing import Optional, Dict, Any
from .repo_dynamo import DynamoRepo

def pk_user(user_id: str) -> str:
    return f"USER#{user_id}"

SK_PROFILE = "PROFILE"

def upsert_profile(repo: DynamoRepo, user_id: str, name: str) -> None:
    if not user_id:
        raise ValueError("user_id required")
    if not name:
        raise ValueError("name required")

    repo.put(
        pk=pk_user(user_id),
        sk=SK_PROFILE,
        attrs={"name": name},
    )

def fetch_profile(repo: DynamoRepo, user_id: str) -> Optional[Dict[str, Any]]:
    if not user_id:
        raise ValueError("user_id required")
    return repo.get(pk_user(user_id), SK_PROFILE)