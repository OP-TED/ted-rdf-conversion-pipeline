from ted_sws.core.adapters.logger import LoggerFactory, LoggingType
from ted_sws.core.model import message
from ted_sws import config

""" 
Here are defined all core/domain messages' handlers
"""


def handler_log(log: message.Log):
    """
    Here is defined the handler for Log Message event
    :param log:
    :return:
    """

    eol = log.format.new_line
    msg = (
            "{title}" + eol + "Messages: " + eol + "{messages}" + eol
    ).format(title=log.title, messages=eol.join(map(lambda m: " - " + m, log.messages)))
    for logging_type_value in config.LOGGING_TYPE.split(","):
        _logger = LoggerFactory.get(LoggingType(logging_type_value), name=logging_type_value + "-logging")
        _logger.log(msg)
    return msg
