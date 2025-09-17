import boto3
import logging

from .creds import CredentialsProvider

logger = logging.getLogger(__name__)


class S3Util:
    def __init__(self, creds: CredentialsProvider):
        self.creds = creds

    def create_bucket(self, bucket_name: str):
        s3 = boto3.resource(
            "s3",
            endpoint_url=self.creds.url,
            region_name=self.creds.region,
            aws_access_key_id=self.creds.access_key_id,
            aws_secret_access_key=self.creds.secret_access_key,
        )

        bucket = s3.Bucket(bucket_name)
        exists = True
        try:
            s3.meta.client.head_bucket(Bucket=bucket_name)
        except:
            exists = False

        if not exists:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": self.creds.region},
            )
            logger.info(f"Bucket '{bucket_name}' created.")
        else:
            logger.info(f"Bucket '{bucket_name}' already exists.")
