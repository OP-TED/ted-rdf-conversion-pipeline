from ted_sws.event_manager.adapters.event_logging_repository import EventLoggingRepository
from ted_sws.event_manager.model.event_message import EventMessage

TEST_DATABASE_NAME = "test_event_logs_database_name"


def test_event_logging_repository_add():
    event_logging_repository = EventLoggingRepository(database_name=TEST_DATABASE_NAME)

    event_message_title = "TEST_EVENT_MESSAGE_TITLE"
    event_message_message = "TEST_EVENT_MESSAGE_MESSAGE"
    event_message = EventMessage(**{"title": event_message_title, "message": event_message_message})
    event_logging_repository.add(event_message)
    result: EventMessage = EventMessage(**event_logging_repository.collection.find_one())
    assert result
    assert result.title == event_message_title
    assert result.message == event_message_message
    event_logging_repository.mongodb_client.drop_database(TEST_DATABASE_NAME)
