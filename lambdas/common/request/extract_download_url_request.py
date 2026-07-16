from common.types.download_data import CustomerDataDownloadUrlRequestData


class InvalidDownloadUrlRequestError(Exception):
    pass


def extract_download_url_request(flask_request):
    payload = flask_request.get_json(silent=True)
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        raise InvalidDownloadUrlRequestError("JSON形式のbodyを指定してください")
    try:
        return CustomerDataDownloadUrlRequestData(
            date_from=payload.get("dateFrom"),
            date_to=payload.get("dateTo"),
        )
    except ValueError as exc:
        raise InvalidDownloadUrlRequestError(str(exc))
