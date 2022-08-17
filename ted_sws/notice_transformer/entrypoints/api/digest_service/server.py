import subprocess

import click

from ted_sws import config
from ted_sws.notice_transformer.entrypoints.api.digest_service.main import API_PREFIX
from ted_sws.event_manager.adapters.event_handler_config import ConsoleLoggerConfig
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.model.event_message import EventMessage
from ted_sws.event_manager.services.logger_from_context import get_env_logger

API_HOST: str = config.ID_MANAGER_API_HOST
API_PORT: int = config.ID_MANAGER_API_PORT


@click.command()
@click.option('-h', '--host', default=API_HOST)
@click.option('-p', '--port', default=API_PORT, type=int)
def api_server_start(host, port):
    bash_script = f"uvicorn --host {host} --port {port} ted_sws.id_manager.entrypoints.api.main:app --reload"
    logger = get_env_logger(EventLogger(ConsoleLoggerConfig(name="API_SERVER")), is_cli=True)
    logger.info(
        EventMessage(message=f"{bash_script}\n###\nSee http://{host}:{port}{API_PREFIX}/docs for API usage.\n###"))
    subprocess.run(bash_script, shell=True, capture_output=True)
