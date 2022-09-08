from ted_sws.event_manager.services.log import log_debug, log_error, log_info


def test_log_info():
    log_info("TEST_INFO_MESSAGE")


def test_log_error():
    log_error("TEST_ERROR_MESSAGE")


def test_log_debug():
    log_debug("TEST_DEBUG_MESSAGE")
