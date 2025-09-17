from dataclasses import InitVar, dataclass, field
from typing import Dict, List
import boto3
import logging
from pathlib import Path
import zipfile

from .enums import Environment
from .utils import run_command
from .creds import CredentialsProvider

logger = logging.getLogger(__name__)


@dataclass
class LambdaParameters:
    function_name: str
    memory_size: int
    timeout_secs: int
    environment: Environment
    handler: str
    env_vars: InitVar[Dict[str, str]]
    allowed_env_vars: List[str] = field(
        default_factory=lambda: [
            "IAC_ENVIRONMENT",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_DEFAULT_REGION",
            "LOCALSTACK_URL",
            "LOCALSTACK_SECRETS_MANAGER_URL",
        ]
    )

    def __post_init__(self, env_vars: Dict[str, str]):
        self._filtered_env_vars = {
            k: v for k, v in env_vars.items() if k in self.allowed_env_vars
        }
        self._filtered_env_vars.update(
            {
                "IAC_ENVIRONMENT": (
                    self.environment.value
                    if isinstance(self.environment, Environment)
                    else str(self.environment)
                ),
            }
        )

    @property
    def filtered_env_vars(self) -> Dict[str, str]:
        return self._filtered_env_vars


class LambdaUtil:
    _infrastructure_dir: Path
    _projects_dir: Path
    creds: CredentialsProvider
    environment: Environment

    def __init__(
        self,
        creds: CredentialsProvider,
        environment: Environment,
        projects_dir: Path,
        infrastructure_dir: Path,
    ):
        self.creds = creds
        self.environment = environment
        self._infrastructure_dir = infrastructure_dir
        self._projects_dir = projects_dir

    def project_path(self, function_name: str):
        return Path.joinpath(self._projects_dir, function_name)


    def _lambda_zip_file(self, lambda_name: str):
        return Path.joinpath(self._infrastructure_dir, f"lambda-{lambda_name}.zip")

    def add_lambda(self, lambda_params: LambdaParameters):

        self._build_and_zip_lambda(
            project_path=self.project_path(""),
            output_zip=self._lambda_zip_file(lambda_params.function_name),
        )

        self._create_lambda(
            function_name=lambda_params.function_name,
            zip_path=self._lambda_zip_file(lambda_params.function_name),
            handler=f"{lambda_params.handler}",
            runtime="dotnet8",
            role="arn:aws:iam::000000000000:role/lambda-role",
            memory_size=lambda_params.memory_size,
            timeout_secs=lambda_params.timeout_secs,
            env_vars=lambda_params.filtered_env_vars,
        )

        self._add_lambda_permission_for_apigateway(
            function_name=lambda_params.function_name, statement_id="apigateway-access"
        )

    def _build_and_zip_lambda(self, project_path: Path, output_zip: str):
        """
        Builds a .NET project in Release mode and zips the output for Lambda deployment.
        :param project_path: Path to the .NET project (.csproj)
        :param output_zip: Path to the output zip file
        """

        project_path = Path(project_path).resolve()
        publish_dir = self._infrastructure_dir / "publish"
        build_cmd = [
            "dotnet",
            "publish",
            str(project_path),
            "-c",
            "Release",
            "-o",
            str(publish_dir),
        ]
        command = " ".join(build_cmd)

        run_command(command)
        if not publish_dir.exists():
            raise FileNotFoundError(
                f"Publish output directory not found: {publish_dir}"
            )

        # 2. Zip the publish output
        logger.info(f"Zipping build output from {publish_dir} to {output_zip}")

        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in publish_dir.rglob("*"):
                zipf.write(file_path, arcname=file_path.relative_to(publish_dir))

        logger.info(f"Lambda zip created at {output_zip}")

    def _create_lambda(
        self,
        function_name: str,
        zip_path: str,
        handler: str,
        runtime: str,
        role: str,
        memory_size: int,
        timeout_secs: int,
        env_vars: dict,
    ):
        lambda_client = boto3.client(
            "lambda",
            endpoint_url=self.creds.url,
            region_name=self.creds.region,
            aws_access_key_id=self.creds.access_key_id,
            aws_secret_access_key=self.creds.secret_access_key,
        )

        with open(zip_path, "rb") as f:
            zip_bytes = f.read()

        try:
            lambda_client.create_function(
                FunctionName=function_name,
                Runtime=runtime,
                Role=role,
                Handler=handler,
                Code={"ZipFile": zip_bytes},
                Environment={"Variables": env_vars},
                MemorySize=memory_size,
                Timeout=timeout_secs,
            )
            logger.info(f"Lambda function '{function_name}' created.")
        except lambda_client.exceptions.ResourceConflictException:
            logger.info(f"Lambda function '{function_name}' already exists.")

    def _add_lambda_permission_for_apigateway(
        self, function_name: str, statement_id: str
    ):
        lambda_client = boto3.client(
            "lambda",
            endpoint_url=self.creds.url,
            region_name=self.creds.region,
            aws_access_key_id=self.creds.access_key_id,
            aws_secret_access_key=self.creds.secret_access_key,
        )

        try:
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId=statement_id,
                Action="lambda:InvokeFunction",
                Principal="apigateway.amazonaws.com",
                SourceArn=f"arn:aws:execute-api:{self.creds.region}:000000000000:local/*/*/*",
            )
            logger.info(
                f"Permission added for API Gateway on Lambda '{function_name}'."
            )
        except lambda_client.exceptions.ResourceConflictException:
            logger.info(
                f"Permission '{statement_id}' already exists for Lambda '{function_name}'."
            )
