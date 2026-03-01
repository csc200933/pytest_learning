import json
import os
from src.repo_dynamo import DynamoRepo
from src import service

def handler(event, context):
    user_id = event.get("pathParameters", {}).get("id")
    body = event.get("body") or "{}"
    data = json.loads(body)

    table_name = os.environ["TABLE_NAME"]
    repo = DynamoRepo(table_name=table_name)

    service.upsert_profile(repo, user_id=user_id, name=data.get("name", ""))

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"ok": True}),
    }