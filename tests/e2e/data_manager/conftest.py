import pytest
from pymongo import MongoClient


@pytest.fixture
def mongodb_client():
    uri = "KEY"
    mongodb_client = MongoClient(uri)
    return mongodb_client