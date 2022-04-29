from typing import List

from ted_sws.event_manager.model import message

""" 
Here are defined all core/domain messages' handlers
"""


def handler_log(log: message.Log):
    """
    Here is defined the handler for Log Message event
    :param log:
    :return:
    """

    eol = message.EOL
    msg = ""
    if log.title:
        msg += ("{title}" + eol).format(title=log.title)
    if log.message:
        if isinstance(log.message, List):
            if not log.title:
                msg += eol
            msg += ("{messages}" + eol).format(
                messages=eol.join(map(lambda m: " - " + m, log.message))
            )
        else:
            msg += log.message
    log.logger.log(msg, log.level)

    return msg
