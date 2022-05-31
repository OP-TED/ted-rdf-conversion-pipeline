import logging
import sys
import threading
import time
import pytest
import re

from ted_sws.event_manager.adapters.log import logger_mongo_handler
from ted_sws.event_manager.adapters.log.logger_mongo_handler import BufferedMongoHandler, MongoHandler


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


# def test_emit(self):
#     self.log.warning('test message')
#     self.force_flush()
#     document = self.handler.collection.find_one(
#         {'message': 'test message', 'level': 'WARNING'})
#     self.assertEqual(document['message'], 'test message')
#     self.assertEqual(document['level'], 'WARNING')
#
#
# def test_emit_exception(self):
#     try:
#         raise Exception('exc1')
#     except:
#         self.log.exception('test message')
#     self.force_flush()
#
#     document = self.handler.collection.find_one(
#         {'message': 'test message', 'level': 'ERROR'})
#     self.assertEqual(document['message'], 'test message')
#     self.assertEqual(document['level'], 'ERROR')
#     self.assertEqual(document['exception']['message'], 'exc1')
#
#
# def test_emit_fail(self):
#     self.handler.collection = ''
#     self.log.warn('test warning')
#     self.force_flush()
#     val = sys.stderr.getvalue()
#     self.assertRegexpMatches(val, r"AttributeError: 'str' object has no attribute '{}'".format(write_many_method))
#
#
# def test_buffer(self):
#     self.force_flush()
#     self.assertEqual(len(self.handler.buffer), 0, "Ensure buffer should be empty")
#
#     self.log.warning('test_buffer message')
#
#     document = self.handler.collection.find_one({'message': 'test_buffer message'})
#     self.assertIsNone(document, "Should not have been written to database")
#     self.assertEqual(len(self.handler.buffer), 1, "Buffer size should be 1")
#
#     self.log.info('test_buffer message')
#     self.log.debug('test_buffer message')
#     self.log.info('test_buffer message')
#
#     doc_amount = self.handler.collection.find({'message': 'test_buffer message'}).count()
#     self.assertEqual(doc_amount, 0, "Nothing should have been written to database")
#     self.assertEqual(len(self.handler.buffer), 4, "Buffer size should be 4")
#
#     self.log.warning('test_buffer message')
#
#     doc_amount = self.handler.collection.find({'message': 'test_buffer message'}).count()
#
#     self.assertEqual(doc_amount, 5, "Buffer size reached, buffer should have been written to database")
#     self.assertEqual(len(self.handler.buffer), 0, "Ensure buffer should be empty")
#
#     self.log.warning('test_buffer message 2')
#
#     document = self.handler.collection.find_one({'message': 'test_buffer message 2'})
#     self.assertIsNone(document, 'Should not have been written to database')
#     self.assertEqual(len(self.handler.buffer), 1, "Buffer size should be 1")
#
#
# def test_buffer_early_flush(self):
#     self.force_flush()
#     self.assertEqual(len(self.handler.buffer), 0, "Ensure buffer should be empty")
#
#     self.log.info('test_buffer_early_flush message')
#
#     document = self.handler.collection.find_one({'message': 'test_buffer_early_flush message'})
#     self.assertIsNone(document, "Should not have been written to database")
#     self.assertEqual(len(self.handler.buffer), 1, "Buffer size should be 1")
#
#     self.log.critical('test_buffer_early_flush message')
#     doc_amount = self.handler.collection.find({'message': 'test_buffer_early_flush message'}).count()
#     self.assertEqual(doc_amount, 2, "2 messages should have been written to database")
#     self.assertEqual(len(self.handler.buffer), 0, "Buffer should now be empty")
#
#     doc_amount = self.handler.collection.find({'message': 'test_buffer_early_flush message',
#                                                'level': 'INFO'}).count()
#     self.assertEqual(doc_amount, 1, "One INFO message should have been written to database")
#
#     doc_amount = self.handler.collection.find({'message': 'test_buffer_early_flush message',
#                                                'level': 'CRITICAL'}).count()
#     self.assertEqual(doc_amount, 1, "One CRITICAL message should have been written to database")
#
#
# def _buffer_periodical_flush(self, is_initialized_in_thread):
#     def initialize():
#         # Creating capped handler
#         self.handler_periodical = BufferedMongoHandler(host=self.host_name,
#                                                        database_name=self.database_name,
#                                                        collection=self.collection_name,
#                                                        buffer_size=5, buffer_periodical_flush_timing=2.0,
#                                                        buffer_early_flush_level=logging.CRITICAL)
#         self.log.removeHandler(self.handler)
#         self.log.addHandler(self.handler_periodical)
#
#     if is_initialized_in_thread:
#         t = threading.Thread(target=initialize)
#         t.start()
#         t.join()
#     else:
#         initialize()
#
#     self.log.info('test periodical buffer')
#     document = self.handler_periodical.collection.find_one({'message': 'test periodical buffer'})
#     self.assertIsNone(document, "Should not have been written to database")  # except if your computer is really slow
#     self.assertEqual(len(self.handler_periodical.buffer), 1, "Buffer size should be 1")
#
#     self.log.info('test periodical buffer')
#     document = self.handler_periodical.collection.find_one({'message': 'test periodical buffer'})
#     self.assertIsNone(document, "Should not have been written to database")
#     self.assertEqual(len(self.handler_periodical.buffer), 2, "Buffer size should be 2")
#
#     time.sleep(2.5)  # wait a bit so the periodical timer thread has kicked off the buffer flush
#
#     document = self.handler_periodical.collection.find_one({'message': 'test periodical buffer'})
#     self.assertIsNotNone(document, "Should not have been written to database")
#     doc_amount = self.handler_periodical.collection.find({'message': 'test periodical buffer'}).count()
#     self.assertEqual(doc_amount, 2, "Should have found 2 documents written to database")
#     self.assertEqual(len(self.handler_periodical.buffer), 0, "Buffer should be empty")
#
#     self.assertTrue(self.handler_periodical.buffer_timer_thread.is_alive())
#     self.handler_periodical.destroy()
#     time.sleep(0.2)  # waiting a tiny bit so that the child thread actually exits
#     self.assertFalse(self.handler_periodical.buffer_timer_thread.is_alive(),
#                      "Child timer thread should be dead by now. Slow computer?")
#
#     # reset to previous
#     self.log.removeHandler(self.handler_periodical)
#     self.log.addHandler(self.handler)
#
#
# def test_buffer_periodical_flush(self):
#     self._buffer_periodical_flush(is_initialized_in_thread=False)
#
#
# def test_buffer_periodical_flush_init_in_new_thread(self):
#     self._buffer_periodical_flush(is_initialized_in_thread=True)
