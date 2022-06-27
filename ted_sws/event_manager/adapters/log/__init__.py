from ted_sws import RUN_ENV_NAME, RUN_ENV_VAL
import os
from enum import Enum


class LoggedBy(Enum):
    DECORATOR = "decorator"
    WRITER = "writer"


def is_event_loggable() -> bool:
    return os.environ[RUN_ENV_NAME] == RUN_ENV_VAL
