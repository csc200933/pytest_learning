from typing import Any, Dict, Optional

def pk_user(user_id: str) -> str:
    if not user_id:
        raise ValueError("user_id is required.")
    return f"USER#{user_id}"

def sk_profile() -> str:
    return "PROFILE"

def user_profile_item(user_id: str, name: str) -> Dict[str, Any]:
    return {"pk": pk_user(user_id), "sk": sk_profile(), "name": name}

def profile_body(name: Optional[str] = "alice") -> Dict[str, Any]:
    """
    POST /users/{id}/profile の request body 用
    name=None を渡したいときはテスト側で body={} にしてもOK
    """
    if name is None:
        return {}
    return {"name": name}

def profile_response(user_id: str, name: str) -> Dict[str, Any]:
    """
    GET /users/{id}/profile の 200 response body 用（handlerが返すdictに合わせる）
    """
    return user_profile_item(user_id, name)

def error_body(code: str, message: str) -> Dict[str, Any]:
    return {"error": {"code": code, "message": message}}

def ok_body() -> Dict[str, Any]:
    return {"ok": True}