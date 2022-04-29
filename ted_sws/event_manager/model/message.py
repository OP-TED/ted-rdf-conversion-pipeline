from typing import Optional, List, Union
from ted_sws.event_manager.adapters.logger import Logger, logger as root_logger

from pydantic import BaseModel

MESSAGE_TYPE = Union[List[str], str]
EOL = "\n"


class Message(BaseModel):
    title: Optional[str] = None
    message: Optional[MESSAGE_TYPE] = None

    class Config:
        arbitrary_types_allowed = True


class Log(Message):
    name: str = __name__
    level: int = None
    logger: Logger = root_logger
