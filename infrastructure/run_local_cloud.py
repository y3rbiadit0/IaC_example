import sys
from pathlib import Path
import os
from dotenv import load_dotenv
import click
from typing import Dict
import logging

from localstack_lib import LocalStackBuilder, run_command, Environment

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@click.command()
@click.option(
    "--environment",
    type=click.Choice([m.value for m in Environment], case_sensitive=True),
    default=Environment.stage.value,
    help="Select Environment [local | stage | prod]",
)
def build_env(environment):
    infrastructure_dir = Path(__file__).parent.resolve()
    projects_dir = infrastructure_dir.parent.resolve()

    env_vars = load_env(
        environment=environment, root_dir=infrastructure_dir
    )
    logger.info(f"DEVELOPMENT_MODE={environment}")

    run_docker_compose(
        environment=environment,
        infrastructure_dir=infrastructure_dir,
        projects_dir=projects_dir,
        env_vars=env_vars,
    )



def run_docker_compose(
    environment: Environment = Environment.local,
    infrastructure_dir: Path = None,
    projects_dir: Path = None,
    env_vars: Dict = None,
):

    logger.info("🛑 Stopping containers and removing volumes...")
    run_command(
        f"docker-compose -p iac_example down -v",
        env_vars=env_vars,
    )

    logger.info("🚀 Starting containers...")
    run_command(
        f"docker-compose -p iac_example --profile {environment} -f {infrastructure_dir}\\docker-compose.yml build",
        env_vars=env_vars,
    )

    run_command(
        f"docker-compose -p iac_example --profile {environment} -f {infrastructure_dir}\\docker-compose.yml up -d localstack",
        env_vars=env_vars,
    )

    LocalStackBuilder(
        infrastructure_dir=infrastructure_dir,
        projects_dir=projects_dir,
        environment=environment,
        env_vars=env_vars,
    ).build()

    run_command(
        f"docker-compose -p iac_example --profile {environment} -f {infrastructure_dir}\\docker-compose.yml up -d",        env_vars=env_vars,
    )
 


def load_env(environment: Environment, root_dir: Path
) -> Dict:
    dotenv_path = Path.joinpath(root_dir, ".env")
    load_dotenv(dotenv_path)

    env = os.environ.copy()
    env["IAC_ENVIRONMENT"] = environment
    return env


if __name__ == "__main__":
    try:
        build_env()
    except Exception as e:
        logger.info(f"❌ Error: {e}")
        sys.exit(1)
