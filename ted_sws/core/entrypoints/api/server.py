import logging
import subprocess
from typing import Tuple

import click

from ted_sws import config
from ted_sws.event_manager.adapters.logger import Logger, LOG_INFO_LEVEL
from ted_sws.event_manager.domain.message_bus import message_bus
from ted_sws.event_manager.model.message import Log
from ted_sws.core.entrypoints.api.main import API_PREFIX

API_SERVER_LOG_LEVELS: Tuple = ('critical', 'error', 'warning', 'info', 'debug', 'trace')
API_HOST: str = config.API_HOST
API_PORT: int = config.API_PORT


@click.command()
@click.option('-h', '--host', default=API_HOST)
@click.option('-p', '--port', default=API_PORT, type=int)
@click.option('-l', '--log-level', default="info", type=click.Choice(API_SERVER_LOG_LEVELS))
def api_server_start(host, port, log_level):
    logger = Logger(name="API_SERVER", level=LOG_INFO_LEVEL)
    fmt = "[%(asctime)s] - %(name)s - %(levelname)s:\n%(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"
    logger_formatter = logging.Formatter(fmt, date_fmt)
    logger.add_stdout_handler(formatter=logger_formatter)
    log_level_text = f" --log-level {log_level}" if log_level else ""
    bash_script = f"uvicorn --host {host} --port {port}{log_level_text} ted_sws.core.entrypoints.api.main:app --reload"
    message_bus.handle(Log(
        message=f"{bash_script}\n###\nSee http://{host}:{port}{API_PREFIX}/docs for API usage.\n###",
        logger=logger)
    )
    subprocess.run(bash_script, shell=True, capture_output=True)
