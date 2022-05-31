import logging

import pytest

from ted_sws.event_manager.adapters.log import logger_mongo_handler
from ted_sws.event_manager.adapters.log.logger_mongo_handler import MongoHandler


def test_logger_mongo_handler(mongo_handler):
    assert isinstance(mongo_handler, MongoHandler)


def test_connect_failed(mongodb_client):
    with pytest.raises(Exception):
        logger_mongo_handler._connection = None
        MongoHandler(mongodb_client=mongodb_client,
                     database_name=None,
                     collection=None,
                     fail_silently=True
                     )


def test_emit(mongo_handler, logger):
    logger.addHandler(mongo_handler)
    logger.warning('test message')
    document = mongo_handler.collection.find_one({'message': 'test message', 'level': 'WARNING'})
    assert document
    assert 'test message' in document['message']
    assert 'WARNING' in document['level']


def test_emit_exception(mongo_handler):
    with pytest.raises(Exception):
        document = mongo_handler.collection.find_one({'message': 'test message', 'level': 'ERROR'})
        assert document
        assert 'test message' in document['message']
        assert 'ERROR' in document['level']
        assert 'exc1' in document['exception']['message']


def _contextual_info(mongo_handler, logger):
    logger.addHandler(mongo_handler)
    logger.info('test message with contextual info', extra={'ip': '127.0.0.1', 'host': 'localhost'})
    document = mongo_handler.collection.find_one({'message': 'test message with contextual info', 'level': 'INFO'})
    assert document
    assert 'test message with contextual info' in document['message']
    assert 'INFO' in document['level']
    assert '127.0.0.1' in document['ip']
    assert 'localhost' in document['host']


def test_contextual_info(mongo_handler, logger):
    _contextual_info(mongo_handler, logger)


def test_buffered_contextual_info(buffered_mongo_handler, logger):
    _contextual_info(buffered_mongo_handler, logger)


def _contextual_info_adapter(mongo_handler, logger):
    logger.addHandler(mongo_handler)
    adapter = logging.LoggerAdapter(logger, {'ip': '127.0.0.1', 'host': 'localhost'})
    adapter.info('test message with contextual info')
    document = mongo_handler.collection.find_one({'message': 'test message with contextual info', 'level': 'INFO'})
    assert 'test message with contextual info' in document['message']
    assert 'INFO' in document['level']
    assert '127.0.0.1' in document['ip']
    assert 'localhost' in document['host']


def test_contextual_info_adapter(mongo_handler, logger):
    _contextual_info_adapter(mongo_handler, logger)


def test_buffered_contextual_info_adapter(buffered_mongo_handler, logger):
    _contextual_info_adapter(buffered_mongo_handler, logger)
