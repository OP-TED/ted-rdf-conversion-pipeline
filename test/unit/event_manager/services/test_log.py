from src.ted_sws.event_manager.services.log import log_debug, log_error, log_info, log_warning, log_technical_debug, \
    log_technical_error, log_technical_info, log_technical_warning, log_notice_warning, log_notice_error, \
    log_notice_debug, log_notice_info, log_mapping_package_debug, log_mapping_package_info, log_mapping_package_error, \
    log_mapping_package_warning, log_cli_brief_notice_info, log_cli_brief_notice_error, log_cli_brief_info, \
    log_cli_brief_error


def test_log_info():
    log_info("TEST_INFO_MESSAGE")


def test_log_error():
    log_error("TEST_ERROR_MESSAGE")


def test_log_debug():
    log_debug("TEST_DEBUG_MESSAGE")


def test_log_warning():
    log_warning("TEST_WARNING_MESSAGE")


def test_log_technical_info():
    log_technical_info("TEST_TECHNICAL_INFO_MESSAGE")


def test_log_technical_error():
    log_technical_error("TEST_TECHNICAL_ERROR_MESSAGE")


def test_log_technical_debug():
    log_technical_debug("TEST_TECHNICAL_DEBUG_MESSAGE")


def test_log_technical_warning():
    log_technical_warning("TEST_TECHNICAL_WARNING_MESSAGE")


def test_log_notice_info(notice_id):
    log_notice_info("TEST_NOTICE_INFO_MESSAGE", notice_id=notice_id)


def test_log_notice_error(notice_id):
    log_notice_error("TEST_NOTICE_ERROR_MESSAGE", notice_id=notice_id)


def test_log_notice_debug(notice_id):
    log_notice_debug("TEST_NOTICE_DEBUG_MESSAGE", notice_id=notice_id)


def test_log_notice_warning(notice_id):
    log_notice_warning("TEST_NOTICE_WARNING_MESSAGE", notice_id=notice_id)


def test_log_mapping_package_info(mapping_package_id):
    log_mapping_package_info("TEST_MAPPING_PACKAGE_INFO_MESSAGE", mapping_package_id=mapping_package_id)


def test_log_mapping_package_error(mapping_package_id):
    log_mapping_package_error("TEST_MAPPING_PACKAGE_ERROR_MESSAGE", mapping_package_id=mapping_package_id)


def test_log_mapping_package_debug(mapping_package_id):
    log_mapping_package_debug("TEST_MAPPING_PACKAGE_DEBUG_MESSAGE", mapping_package_id=mapping_package_id)


def test_log_mapping_package_warning(mapping_package_id):
    log_mapping_package_warning("TEST_MAPPING_PACKAGE_WARNING_MESSAGE", mapping_package_id=mapping_package_id)


def test_log_cli_brief_notice_info():
    log_cli_brief_notice_info("TEST_BRIEF_NOTICE_INFO_MESSAGE")


def test_log_cli_brief_notice_error():
    log_cli_brief_notice_error("TEST_BRIEF_NOTICE_ERROR_MESSAGE")


def test_log_cli_brief_info():
    log_cli_brief_info("TEST_BRIEF_INFO_MESSAGE")


def test_log_cli_brief_error():
    log_cli_brief_error("TEST_BRIEF_ERROR_MESSAGE")
