import os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class CredentialsProvider:
    access_key_id: str
    secret_access_key: str
    url: str
    region: str
    secrets_file: str

    @classmethod
    def from_env(cls, root_dir: Path) -> "CredentialsProvider":
        return cls(
            access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
            secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
            url=os.getenv("LOCALSTACK_URL", "http://localhost:4566"),
            region=os.getenv("AWS_DEFAULT_REGION", "eu-west-1"),
            secrets_file=Path.joinpath(root_dir, "secrets.json"),
        )
