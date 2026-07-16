import os

from common.repository.cancel_download_repository import CancelDownloadRepository
from common.service.csv_service import build_csv_bytes
from common.service.flow_log_service import extract_final_check_customer_data
from common.service.s3_service import S3Service
from common.service.time_service import get_jst, parse_text_to_date
from common.types.download_data import (
    CUSTOMER_DATA_DOWNLOAD_OUTPUT_COLUMNS,
    CustomerDataDownloadUrlRequestData,
)


class UseCaseError(Exception):
    pass


class InvalidDownloadUrlDataError(UseCaseError):
    pass


def _to_slashed_date(value):
    return parse_text_to_date(value, fmt="%Y%m%d", out_fmt="%Y/%m/%d") or ""


def _build_row(source_row):
    row = {column: "" for column in CUSTOMER_DATA_DOWNLOAD_OUTPUT_COLUMNS}
    customer_data = extract_final_check_customer_data(source_row)

    row["ﾏｲﾍﾟｰｼﾞ受付日時"] = (
        parse_text_to_date(source_row.get("start_time"), out_fmt="%Y/%m/%d %H:%M:%S")
        or ""
    )
    row["顧客コード"] = str(customer_data.get("CUST_CD") or "").strip()
    row["契約No"] = str(customer_data.get("KYK_NO") or "").strip()
    row["顧客名カナ(契約者)"] = str(customer_data.get("SW_CUST_KNM") or "").strip()
    row["生年月日(契約者)"] = _to_slashed_date(customer_data.get("BIRTH_DT"))
    row["電話番号1(契約者)"] = str(customer_data.get("TEL1") or "").strip()
    row["電話番号2(契約者)"] = str(customer_data.get("TEL2") or "").strip()
    row["郵便番号(契約者)"] = str(customer_data.get("POST_CD") or "").strip()
    row["契約品目コード(浄水器)"] = str(customer_data.get("ITEM") or "").strip()
    row["契約次回交換日"] = _to_slashed_date(customer_data.get("NEXTCHG_DT"))
    return row


class CustomerDataDownloadUrlUseCase:
    def __init__(self):
        self.bucket_name = os.getenv("CUSTOMER_DATA_BUCKET_NAME")
        self.download_url_expires_seconds = os.getenv("DOWNLOAD_URL_EXPIRES_SECONDS")
        self.download_source_table_name = os.getenv("DOWNLOAD_SOURCE_TABLE_NAME")
        self.customer_data_company = os.getenv("CUSTOMER_DATA_COMPANY")

    def execute(self, request_data: CustomerDataDownloadUrlRequestData):
        expires_seconds = int(self.download_url_expires_seconds)
        source_company = str(self.customer_data_company).strip()
        download_source_pk = "CompanyName#{}".format(source_company)
        table_name = str(self.download_source_table_name).strip()

        source_rows = CancelDownloadRepository().query_completed_rows(
            table_name,
            date_from=request_data.date_from,
            date_to=request_data.date_to,
            pk_value=download_source_pk,
        )
        if not source_rows:
            raise InvalidDownloadUrlDataError("対象期間のダウンロードデータがありません")

        rows = [_build_row(source_row) for source_row in source_rows]

        csv_bytes = build_csv_bytes(
            rows,
            CUSTOMER_DATA_DOWNLOAD_OUTPUT_COLUMNS,
            encoding="cp932",
            include_header=False,
        )

        timestamp = get_jst("text")
        date_text = str(timestamp)[:8]
        object_key = "{}/{}/{}/{}_{}.csv".format(
            source_company,
            "download",
            date_text,
            source_company,
            timestamp,
        )

        s3_service = S3Service()
        s3_service.put_object(
            bucket=self.bucket_name,
            key=object_key,
            body=csv_bytes,
            content_type="text/csv; charset=shift_jis",
        )

        download_url = s3_service.generate_presigned_get_object_url(
            bucket=self.bucket_name,
            key=object_key,
            expires_in=expires_seconds,
        )

        return {
            "downloadUrl": download_url,
            "downloadMethod": "GET",
            "bucket": self.bucket_name,
            "objectKey": object_key,
            "tableName": table_name,
            "rowCount": len(rows),
            "dateFrom": request_data.date_from,
            "dateTo": request_data.date_to,
            "expiresIn": expires_seconds,
        }
