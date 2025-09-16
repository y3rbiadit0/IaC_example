import logging
from pathlib import Path

import boto3

from .enums import Environment
from .creds import LocalStackCreds

logger = logging.getLogger(__name__)


class APIGatewayUtil:
    creds: LocalStackCreds
    environment: Environment
    aws_localstack_dir: Path

    def __init__(
        self, creds: LocalStackCreds, aws_localstack_dir: Path, environment: Environment
    ):
        self.creds = creds
        self.aws_localstack_dir: Path = aws_localstack_dir
        self.environment = environment

    @property
    def _api_gateway_stage_file(self):
        return Path.joinpath(
            self.aws_localstack_dir, "tpn-stage-swagger-apigateway.json"
        )

    def create_api_gateway(self):
        api_id = self._create_api_with_custom_id(
            name=f"tpn-{self.environment}", custom_id=f"tpn-{self.environment}"
        )
        self._import_api_definition(
            api_id=api_id, json_file=self._api_gateway_stage_file
        )
        self._deploy_api_gateway(api_id, stage_name=self.environment)

    def _create_api_with_custom_id(self, name: str, custom_id: str) -> str:
        apigateway = boto3.client(
            "apigateway",
            endpoint_url=self.creds.url,
            region_name=self.creds.region,
            aws_access_key_id=self.creds.access_key_id,
            aws_secret_access_key=self.creds.secret_access_key,
        )

        response = apigateway.create_rest_api(
            name=name, tags={"_custom_id_": custom_id}
        )
        api_id = response["id"]
        logger.info(f"API Gateway created with custom ID: {api_id}")
        return api_id

    def _import_api_definition(self, api_id: str, json_file: str):
        apigateway = boto3.client(
            "apigateway",
            endpoint_url=self.creds.url,
            region_name=self.creds.region,
            aws_access_key_id=self.creds.access_key_id,
            aws_secret_access_key=self.creds.secret_access_key,
        )

        with open(json_file, "r") as f:
            body = f.read()

        apigateway.put_rest_api(restApiId=api_id, mode="overwrite", body=body)
        logger.info(f"API definition imported into API {api_id}")

    def _deploy_api_gateway(self, api_id: str, stage_name: str):
        apigateway = boto3.client(
            "apigateway",
            endpoint_url=self.creds.url,
            region_name=self.creds.region,
            aws_access_key_id=self.creds.access_key_id,
            aws_secret_access_key=self.creds.secret_access_key,
        )

        apigateway.create_deployment(restApiId=api_id, stageName=stage_name)
        logger.info(f"API Gateway '{api_id}' deployed to stage '{stage_name}'.")
