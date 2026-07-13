import boto3


class ParameterStoreService:
    def __init__(self, region_name=None):
        self.ssm_client = boto3.client("ssm", region_name=region_name)

    def get_value(self, parameter_name):
        target_parameter_name = str(parameter_name or "").strip()
        if not target_parameter_name:
            return ""
        response = self.ssm_client.get_parameter(
            Name=target_parameter_name,
            WithDecryption=False,
        )
        value = str(response["Parameter"]["Value"] or "").strip()
        return value
