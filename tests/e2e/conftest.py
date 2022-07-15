import pytest
from pymongo import MongoClient

from ted_sws import config


@pytest.fixture
def mongodb_client():
    uri = config.MONGO_DB_AUTH_URL
    mongodb_client = MongoClient(uri)
    return mongodb_client
