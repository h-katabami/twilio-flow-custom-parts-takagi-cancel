import boto3
from boto3.dynamodb.conditions import Key


class DynamoDBService:
    def __init__(self, region_name=None):
        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)

    def get_table_resource(self, table_name):
        return self.dynamodb.Table(table_name)

    def build_key_eq_expression(self, key_name, key_value):
        return Key(key_name).eq(key_value)

    def build_key_between_expression(self, key_name, start_value, end_value):
        return Key(key_name).between(start_value, end_value)

    def query_latest_record(self, table, key_name, key_value, index_name=None):
        query_kwargs = {
            "KeyConditionExpression": Key(key_name).eq(key_value),
            "ScanIndexForward": False,
            "Limit": 1,
        }
        if index_name:
            query_kwargs["IndexName"] = index_name

        response = table.query(**query_kwargs)
        items = response.get("Items", [])
        if not items:
            return {}
        return dict(items[0])

    def query_record_count(self, table, key_name, key_value, index_name=None):
        query_kwargs = {
            "KeyConditionExpression": Key(key_name).eq(key_value),
            "Select": "COUNT",
        }
        if index_name:
            query_kwargs["IndexName"] = index_name

        response = table.query(**query_kwargs)
        return int(response.get("Count", 0))
