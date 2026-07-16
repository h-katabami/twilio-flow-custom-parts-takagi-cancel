from common.service.dynamodb_service import DynamoDBService
from common.service.flow_log_service import (
    extract_final_check_customer_data,
    reached_ending,
)

MANAGEMENT_SCREEN_INDEX = "ManagementScreenIndex"


class CancelDownloadRepository:
    def __init__(self):
        self.dynamodb_service = DynamoDBService()

    def _fetch_full_row(self, table, indexed_row):
        # GSI の射影には api / user_inputs が含まれないため、本体を取り直す。
        response = table.get_item(
            Key={
                "PK": indexed_row.get("PK"),
                "SK": indexed_row.get("SK"),
            }
        )
        row = response.get("Item")
        if not isinstance(row, dict):
            return None
        return row

    def query_completed_rows(self, table_name, date_from, date_to, pk_value):
        table = self.dynamodb_service.get_table_resource(table_name)
        pk_condition = self.dynamodb_service.build_key_eq_expression(
            "PK", str(pk_value)
        )
        start_time_condition = self.dynamodb_service.build_key_between_expression(
            "start_time", str(date_from).strip(), str(date_to).strip()
        )
        query_kwargs = {
            "IndexName": MANAGEMENT_SCREEN_INDEX,
            "KeyConditionExpression": pk_condition & start_time_condition,
        }

        rows = []
        while True:
            response = table.query(**query_kwargs)
            for indexed_row in response.get("Items", []):
                row = self._fetch_full_row(table, indexed_row)
                if row is None:
                    continue
                if not extract_final_check_customer_data(row):
                    continue
                if not reached_ending(row):
                    continue
                rows.append(row)

            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break
            query_kwargs["ExclusiveStartKey"] = last_evaluated_key

        return rows
