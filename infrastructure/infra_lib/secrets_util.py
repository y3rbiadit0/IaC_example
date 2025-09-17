import json
import os
from typing import Dict
import boto3
import logging

from .creds import CredentialsProvider

logger = logging.getLogger(__name__)


class SecretsManagerUtil:
    def __init__(self, creds: CredentialsProvider):
        self.creds = creds

    def create_secrets(self):
        if not os.path.exists(self.creds.secrets_file):
            logger.info(
                f"No secrets file found at '{self.creds.secrets_file}', skipping secrets creation."
            )
            return

        with open(self.creds.secrets_file, "r") as f:
            secrets: Dict = json.load(f)

        client = boto3.client(
            "secretsmanager",
            endpoint_url=self.creds.url,
            region_name=self.creds.region,
            aws_access_key_id=self.creds.access_key_id,
            aws_secret_access_key=self.creds.secret_access_key,
        )

        for name, value in secrets.items():
            try:
                value = client.create_secret(Name=name, SecretString=json.dumps(value))
                logger.info(f"Secret '{name}' created.")
            except client.exceptions.ResourceExistsException:
                logger.info(f"Secret '{name}' already exists.")
