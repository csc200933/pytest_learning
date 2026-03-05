# src/handler.py
import json
import os
from src.repo_dynamo import DynamoRepo
from src import service

import logging
logger = logging.getLogger(__name__)

def _json(status: int, body: dict):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }

def _error(status: int, code: str, message: str):
    return _json(status, {"error": {"code": code, "message": message}})


def handler(event, context):
    try:
        method = event.get("httpMethod")
        user_id = (event.get("pathParameters") or {}).get("id")
        table_name = os.environ["TABLE_NAME"]
        repo = DynamoRepo(table_name=table_name)

        bad = _error(400, "BAD_REQUEST", "bad request")

        if method == "POST":
            try:
                data = json.loads(event.get("body") or "{}")
            except Exception:
                return bad
            
            name = data.get("name")
            if not user_id or not name:
                return bad

            if not (1 <= len(name) <= 50):
                return bad

            service.upsert_profile(repo, user_id=user_id, name=name)
            return _json(200, {"ok": True})

        if method == "GET":
            item = service.fetch_profile(repo, user_id=user_id)
            if item is None:
                return _error(404, "NOT_FOUND", "not found")
            return _json(200, item)

        return _error(405, "METHOD_NOT_ALLOWED", "method not allowed")
    except Exception:
        logger.exception("Unhandled error")
        return _error(500, "INTERNAL_ERROR", "internal server error")