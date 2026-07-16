from base64 import b64decode

from common.request.authorize_request import is_company_allowed
from common.request.extract_download_url_request import (
    InvalidDownloadUrlRequestError,
    extract_download_url_request,
)
from common.response.event_response import (
    flask_json_response,
    forbidden,
    internal_error,
)
from common.service.logger import error, info, warn
from common.usecase.customer_data_download_url_usecase import (
    CustomerDataDownloadUrlUseCase,
    InvalidDownloadUrlDataError,
)
from flask import Flask, request

ALLOWED_COMPANIES = ["tact", "takagi"]
DOWNLOAD_ROUTE = "/services/TakagiCancel/customer-data/download"

app = Flask(__name__)


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


def _invoke_http_with_flask(event):
    http_event = event or {}
    body = http_event.get("body")
    if body is None:
        request_body = b""
    elif http_event.get("isBase64Encoded"):
        if isinstance(body, str):
            request_body = b64decode(body)
        elif isinstance(body, (bytes, bytearray)):
            request_body = bytes(body)
        else:
            request_body = b64decode(str(body))
    elif isinstance(body, (bytes, bytearray)):
        request_body = bytes(body)
    else:
        request_body = str(body).encode("utf-8")

    headers = {
        key: value
        for key, value in (http_event.get("headers") or {}).items()
        if value is not None
    }

    with app.test_client() as client:
        response = client.open(
            path=http_event.get("path") or "/",
            method=http_event.get("httpMethod") or "GET",
            headers=headers,
            query_string=http_event.get("queryStringParameters") or {},
            data=request_body,
        )

    return {
        "statusCode": response.status_code,
        "headers": dict(response.headers),
        "body": response.get_data(as_text=True),
        "isBase64Encoded": False,
    }


def lambda_handler(event, context):
    try:
        claims = (
            (event or {})
            .get("requestContext", {})
            .get("authorizer", {})
            .get("claims", {})
        )
        company = claims.get("custom:company")
        info(
            "http request: method={}, path={}, company={}".format(
                (event or {}).get("httpMethod"),
                (event or {}).get("path"),
                company,
            )
        )

        if not is_company_allowed(event, ALLOWED_COMPANIES):
            warn(
                "company is not allowed: company={}, allowed={}".format(
                    company,
                    ALLOWED_COMPANIES,
                )
            )
            return forbidden(message="Forbidden", code="FORBIDDEN")

        return _invoke_http_with_flask(event)
    except Exception as exc:
        error("unhandled request error: {}".format(exc), exc=exc)
        return internal_error(
            message="リクエスト処理中にエラーが発生しました",
            code="REQUEST_ERROR",
        )


@app.route(DOWNLOAD_ROUTE, methods=["POST"])
def create_download_url():
    try:
        request_data = extract_download_url_request(request)
        result = CustomerDataDownloadUrlUseCase().execute(request_data)
        info(
            "download url generated: rowCount={}, objectKey={}".format(
                result.get("rowCount"),
                result.get("objectKey"),
            )
        )
        return flask_json_response(200, result)
    except (InvalidDownloadUrlRequestError, InvalidDownloadUrlDataError) as exc:
        warn("download url validation error: {}".format(exc))
        return flask_json_response(400, {"message": str(exc)})
    except Exception as exc:
        error("unhandled download url error: {}".format(exc), exc=exc)
        return flask_json_response(
            500, {"message": "ダウンロードURLの生成中にエラーが発生しました"}
        )


if __name__ == "__main__":
    app.run(debug=True)
