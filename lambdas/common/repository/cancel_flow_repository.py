import os

from common.service.dynamodb_service import DynamoDBService
from common.service.logger import warn
from common.service.parameter_store_service import ParameterStoreService
from common.service.time_service import parse_text_to_date


class CancelFlowRepository:
    def __init__(self):
        self.dynamodb_service = DynamoDBService()
        parameter_name = os.getenv("TABLE_NAME_PARAMETER_PATH")
        self.parameter_store_service = ParameterStoreService()
        self.table_name = self.parameter_store_service.get_value(parameter_name)
        if not self.table_name:
            warn("table name is empty. set TABLE_NAME_PARAMETER_PATH")
            raise RuntimeError("table name is empty")
        self.table = self.dynamodb_service.get_table_resource(self.table_name)

    def _with_parsed_dates(self, item):
        if not item:
            return {}
        item["PRECHG_DT"] = parse_text_to_date(item.get("PRECHG_DT"), "%Y%m%d")
        item["NEXTCHG_DT"] = parse_text_to_date(
            item.get("NEXTCHG_DT"), "%Y%m%d"
        )
        return item

    def get_by_cust_cd(self, cust_cd):
        item = self.dynamodb_service.query_latest_record(
            self.table,
            "CUST_CD",
            cust_cd,
        )
        return self._with_parsed_dates(item)

    def count_by_cust_cd(self, cust_cd):
        return self.dynamodb_service.query_record_count(
            self.table,
            "CUST_CD",
            cust_cd,
        )

    def get_by_tel(self, tel):
        item = self.dynamodb_service.query_latest_record(
            self.table,
            "TEL1",
            tel,
            index_name="index_TEL1",
        )
        if not item:
            item = self.dynamodb_service.query_latest_record(
                self.table,
                "TEL2",
                tel,
                index_name="index_TEL2",
            )
        return self._with_parsed_dates(item)

    def count_by_tel(self, tel):
        count = self.dynamodb_service.query_record_count(
            self.table,
            "TEL1",
            tel,
            index_name="index_TEL1",
        )
        if count == 0:
            count = self.dynamodb_service.query_record_count(
                self.table,
                "TEL2",
                tel,
                index_name="index_TEL2",
            )
        return count

    def find_customer(self, event_data):
        item = {}
        matched_count = 0
        if event_data.cust_cd:
            matched_count = self.count_by_cust_cd(event_data.cust_cd)
            item = self.get_by_cust_cd(event_data.cust_cd)
        if not item and event_data.tel1:
            matched_count = self.count_by_tel(event_data.tel1)
            item = self.get_by_tel(event_data.tel1)
        if not item and event_data.tel2:
            matched_count = self.count_by_tel(event_data.tel2)
            item = self.get_by_tel(event_data.tel2)
        return item, matched_count
