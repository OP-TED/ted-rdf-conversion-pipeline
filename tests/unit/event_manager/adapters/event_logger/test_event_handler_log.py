import os


def test_event_handler(event_handler, event_message, severity_level_info):
    event_handler.log(severity_level_info, event_message)

    caller_name = event_handler._caller_name(event_message)
    assert caller_name

    caller_name_value = "CALLER_NAME"
    event_message.caller_name = caller_name_value
    caller_name = event_handler._caller_name(event_message)
    assert caller_name == caller_name_value


def test_console_handler_log(caplog, console_handler, severity_level_info, event_message, output_not_briefly_key):
    console_handler.log(severity_level_info, event_message)
    assert event_message.message in caplog.text
    assert output_not_briefly_key in caplog.text


def test_console_handler_log_briefly(caplog, console_handler, severity_level_info, event_message,
                                     output_not_briefly_key, log_settings):
    log_settings.briefly = True
    console_handler.log(severity_level_info, event_message, log_settings)
    assert event_message.message in caplog.text
    assert output_not_briefly_key not in caplog.text


def test_file_handler_log(file_handler, severity_level_debug, event_message):
    file_handler.log(severity_level_debug, event_message)
    assert event_message.message in open(file_handler.filepath).read()
    os.remove(file_handler.filepath)


def test_null_handler_log(null_handler, severity_level_info, event_message):
    assert null_handler


def test_mongodb_handler_log(mongodb_handler, logs_database_name, severity_level_error, event_message,
                             notice_event_message, mapping_suite_event_message, technical_event_message,
                             event_logging_repository, notice_event_repository, mapping_suite_event_repository,
                             technical_event_repository):
    log: dict

    result = mongodb_handler.log(severity_level_error, event_message)
    assert result
    log = event_logging_repository.collection.find_one()
    assert log['message'] == event_message.message

    result = mongodb_handler.log(severity_level_error, notice_event_message)
    assert result
    log = notice_event_repository.collection.find_one()
    assert log['message'] == notice_event_message.message

    result = mongodb_handler.log(severity_level_error, mapping_suite_event_message)
    assert result
    log = mapping_suite_event_repository.collection.find_one()
    assert log['message'] == mapping_suite_event_message.message

    result = mongodb_handler.log(severity_level_error, technical_event_message)
    assert result
    log = technical_event_repository.collection.find_one()
    assert log['message'] == technical_event_message.message

    mongodb_handler.mongodb_client.drop_database(logs_database_name)
