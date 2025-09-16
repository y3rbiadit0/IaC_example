import boto3
import logging
from dataclasses import dataclass
from typing import Optional, List

from .creds import LocalStackCreds


logger = logging.getLogger(__name__)



@dataclass
class QueueConfig:
    name: str
    visibility_timeout: int
    lambda_target: str
    batch_size: int = 10
    batch_window: Optional[int] = None
    report_batch_item_failures: bool = False

class QueuesUtil:
    def __init__(self, creds: LocalStackCreds):
        self.creds = creds


    def create_queues(self, queues: List[QueueConfig]):
        sqs = boto3.client(
            "sqs",
            endpoint_url=self.creds.url,
            region_name=self.creds.region,
            aws_access_key_id=self.creds.access_key_id,
            aws_secret_access_key=self.creds.secret_access_key,
        )

        for q in queues:
            sqs.create_queue(
                QueueName=q.name,
                Attributes={
                    "FifoQueue": "true",
                    "ContentBasedDeduplication": "true",
                    "VisibilityTimeout": str(q.visibility_timeout),
                },
            )
            logger.info(f"Queue created: {q.name} (Visibility {q.visibility_timeout}s)")

            # Optional: attach queue as Lambda event source mapping
            lambda_client = boto3.client(
                "lambda",
                endpoint_url=self.creds.url,
                region_name=self.creds.region,
                aws_access_key_id=self.creds.access_key_id,
                aws_secret_access_key=self.creds.secret_access_key,
            )

            lambda_client.create_event_source_mapping(
                EventSourceArn=f"arn:aws:sqs:{self.creds.region}:000000000000:{q.name}",
                FunctionName=q.lambda_target,
                BatchSize=q.batch_size,
                MaximumBatchingWindowInSeconds=q.batch_window or 0,
                FunctionResponseTypes=["ReportBatchItemFailures"]
                if q.report_batch_item_failures
                else [],
            )
            logger.info(f"Queue {q.name} linked to Lambda {q.lambda_target}")