import json
from typing import Any, Dict, Optional

def apigw_v1_event(
    method: str,
    path: str,
    *,
    path_params: Optional[Dict[str, str]] = None,
    query_params: Optional[Dict[str, str]] = None,
    body_obj: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    return {
        "resource": path,
        "path": path,
        "httpMethod": method,
        "headers": {"Content-Type": "application/json", **(headers or {})},
        "queryStringParameters": query_params or None,
        "pathParameters": path_params or None,
        "requestContext": {
            "resourcePath": path,
            "httpMethod": method,
            "path": path,
            "stage": "test",
        },
        "body": json.dumps(body_obj) if body_obj is not None else None,
        "isBase64Encoded": False,
    }