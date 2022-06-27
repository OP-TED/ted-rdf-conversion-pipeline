from ted_sws.event_manager.adapters.log.log_writer import LogWriter


def test_log_writer(mongodb_client):
    log_writer = LogWriter(mongodb_client)
    result = log_writer.save("TITLE", "MESSAGE", {})
    assert result
