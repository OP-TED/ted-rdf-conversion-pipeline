from ted_sws.event_manager.adapters.logger import Logger, LOG_INFO_LEVEL
import logging


def test_logger(caplog):
    logger = Logger(name="ID_MANAGER_API_SERVER", level=LOG_INFO_LEVEL)
    assert not logger.get_handlers()
    assert not logger.init_handlers()

    logger.add_console_handler(formatter=logging.Formatter(
        "[%(asctime)s] - %(name)s - %(levelname)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    ))
    assert logger.get_handlers()

    logger.get_logger().propagate = True
    logger.log("TEST_MESSAGE", LOG_INFO_LEVEL)

    assert "TEST_MESSAGE" in caplog.text
