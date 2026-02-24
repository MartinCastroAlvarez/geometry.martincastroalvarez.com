from __future__ import annotations

import json
from typing import Any


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Auth",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    }
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 204, "headers": headers, "body": ""}
    body = json.dumps({"message": "geometry api"})
    return {"statusCode": 200, "headers": headers, "body": body}
