# src/handler.py
import json
import os
from src.repo_dynamo import DynamoRepo
from src import service

def _json(status: int, body: dict):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }

def handler(event, context):
    method = event.get("httpMethod")
    user_id = (event.get("pathParameters") or {}).get("id")
    table_name = os.environ["TABLE_NAME"]
    repo = DynamoRepo(table_name=table_name)

    bad = _json(400, {"message": "bad request"})
    if method == "POST":
        try:
            data = json.loads(event.get("body") or "{}")
        except Exception:
            return bad
        
        name = data.get("name")
        if not user_id or not name:
            return bad

        service.upsert_profile(repo, user_id=user_id, name=name)
        return _json(200, {"ok": True})

    if method == "GET":
        item = service.fetch_profile(repo, user_id=user_id)
        if item is None:
            return _json(404, {"message": "not found"})
        return _json(200, item)

    return _json(405, {"message": "method not allowed"})