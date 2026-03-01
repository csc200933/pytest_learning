from typing import Any, Dict

def pk_user(user_id: str) -> str:
    return f"USER#{user_id}"

def sk_profile() -> str:
    return "PROFILE"

def user_profile_item(user_id: str, name: str) -> Dict[str, Any]:
    return {"pk": pk_user(user_id), "sk": sk_profile(), "name": name}