import boto3


class S3Service:
    def __init__(self, region_name=None):
        self.s3_client = boto3.client("s3", region_name=region_name)

    def put_object(self, bucket, key, body, content_type=None):
        put_kwargs = {
            "Bucket": bucket,
            "Key": key,
            "Body": body,
        }
        if content_type:
            put_kwargs["ContentType"] = content_type
        self.s3_client.put_object(**put_kwargs)

    def generate_presigned_get_object_url(self, bucket, key, expires_in):
        return self.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": bucket,
                "Key": key,
            },
            ExpiresIn=expires_in,
            HttpMethod="GET",
        )
