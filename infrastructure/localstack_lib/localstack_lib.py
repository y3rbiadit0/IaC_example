import os
from pathlib import Path
import logging
from typing import Dict


from .creds import LocalStackCreds
from .eventbridge_util import EventBridgeStackConfig, EventBridgeUtil
from .lambda_util import LambdaParameters, LambdaUtil
from .queues_util import QueueConfig, QueuesUtil
from .s3_util import S3Util
from .secrets_util import SecretsManagerUtil
from .api_gateway_util import APIGatewayUtil
from .enums import Environment

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class LocalStackBuilder:
    lambda_util: LambdaUtil
    queues_util: QueuesUtil
    s3_util: S3Util
    eventbridge_util: EventBridgeUtil
    secrets_util: SecretsManagerUtil
    api_gateway_util: APIGatewayUtil
    env_vars: Dict[str, str]

    def __init__(
        self,
        infrastructure_dir: Path,
        projects_dir: Path,
        environment: Environment,
        env_vars: Dict[str, str],
    ):
        self.infrastructure_dir = infrastructure_dir
        self.projects_dir = projects_dir
        self._aws_localstack_dir = Path.joinpath(
            self.infrastructure_dir, "aws_localstack"
        )

        self.creds = LocalStackCreds.from_env(root_dir=self._aws_localstack_dir)
        self.environment = environment
        self.env_vars = env_vars

        self.secrets_util = SecretsManagerUtil(creds=self.creds)
        self.s3_util = S3Util(creds=self.creds)
        self.queues_util = QueuesUtil(creds=self.creds)
        self.api_gateway_util = APIGatewayUtil(
            creds=self.creds,
            aws_localstack_dir=self._aws_localstack_dir,
            environment=self.environment,
        )
        self.lambda_util = LambdaUtil(
            creds=self.creds,
            environment=self.environment,
            projects_dir=self.projects_dir,
            infrastructure_dir=self.infrastructure_dir,
        )
        self.eventbridge_util = EventBridgeUtil(
            creds=self.creds,
            aws_localstack_dir=self._aws_localstack_dir,
            environment=environment,
        )

    def build(self):
        self.secrets_util.create_secrets()

        if self.environment == Environment.stage:
            self.create_lambdas()
            self.api_gateway_util.create_api_gateway()

    def create_lambdas(self):
        self.lambda_util.add_lambda(
            lambda_params=LambdaParameters(
                function_name="iac-example-fibonacci",
                memory_size=256,
                timeout_secs=900,
                environment=self.environment,
                env_vars=self.env_vars,
                handler="IaC_example::IaC_example.LambdaApp::HandlerAsync"
            )
        )

    def create_queues(self):
        tpn_regulation_fifo = QueueConfig(
            name=os.getenv("REGULATION_SQS_CODE_NAME"),
            lambda_target="tpn-regulation",
            batch_size=10,
            batch_window=None,
            visibility_timeout=300,
        )
        tpn_ddd_parser_fifo = QueueConfig(
            name=os.getenv("DDDPARSER_SQS_CODE_NAME"),
            lambda_target="tpn-ddd-parser",
            batch_size=10,
            batch_window=None,
            visibility_timeout=600,
        )
        queues = [tpn_regulation_fifo, tpn_ddd_parser_fifo]
        self.queues_util.create_queues(queues)
