# src/repo_dynamo.py
import boto3
from typing import Any, Dict, Optional

class DynamoRepo:
    def __init__(self, table_name: str, dynamodb_resource=None):
        self._dynamodb = dynamodb_resource or boto3.resource("dynamodb")
        self._table = self._dynamodb.Table(table_name)

    def put(self, pk: str, sk: str, attrs: Dict[str, Any]) -> None:
        self._table.put_item(Item={"pk": pk, "sk": sk, **attrs})

    def get(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        resp = self._table.get_item(Key={"pk": pk, "sk": sk})
        return resp.get("Item")
    
    def update_profile_name_if_exists(self, pk: str, sk: str, name: str) -> None:
        # pk+sk が存在する場合だけ更新（存在しない場合は ConditionalCheckFailed）
        self._table.update_item(
            Key={"pk": pk, "sk": sk},
            UpdateExpression="SET #n = :name",
            ExpressionAttributeNames={"#n": "name"},
            ExpressionAttributeValues={":name": name},
            ConditionExpression="attribute_exists(pk) AND attribute_exists(sk)",
        )