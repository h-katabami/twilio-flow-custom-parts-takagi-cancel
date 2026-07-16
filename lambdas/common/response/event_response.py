import json


def flask_json_response(status_code, payload, headers=None):
    merged_headers = {"Content-Type": "application/json; charset=utf-8"}
    if headers:
        merged_headers.update(headers)

    return (
        json.dumps(payload, ensure_ascii=False),
        status_code,
        merged_headers,
    )


def build_response(status_code, code, message, data=None, headers=None):
    body = {
        "code": code,
        "message": message,
        "data": data,
    }
    merged_headers = {
        "Content-Type": "application/json; charset=utf-8",
    }
    if headers:
        merged_headers.update(headers)

    return {
        "statusCode": status_code,
        "headers": merged_headers,
        "body": json.dumps(body, ensure_ascii=False),
    }


def forbidden(data=None, message="forbidden", code="FORBIDDEN", headers=None):
    return build_response(403, code, message, data=data, headers=headers)


def internal_error(
    data=None,
    message="internal server error",
    code="INTERNAL_SERVER_ERROR",
    headers=None,
):
    return build_response(500, code, message, data=data, headers=headers)
