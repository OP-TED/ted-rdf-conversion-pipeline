from typing import Optional, List

from pydantic import BaseModel


class MessageFormat(BaseModel):
    new_line: str = "\n"


class Message(BaseModel):
    title: Optional[str] = None
    messages: Optional[List[str]] = []
    format: Optional[MessageFormat] = MessageFormat()


class Log(Message):
    pass
