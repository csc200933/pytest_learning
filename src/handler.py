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

    if method == "POST":
        data = json.loads(event.get("body") or "{}")
        service.upsert_profile(repo, user_id=user_id, name=data.get("name", ""))
        return _json(200, {"ok": True})

    if method == "GET":
        item = service.fetch_profile(repo, user_id=user_id)
        if item is None:
            return _json(404, {"message": "not found"})
        return _json(200, item)

    return _json(405, {"message": "method not allowed"})