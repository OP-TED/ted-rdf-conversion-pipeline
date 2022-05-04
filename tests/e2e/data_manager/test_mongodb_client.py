from pymongo import MongoClient

from ted_sws import config


def test_mongodb_client(notice_2016):
    uri = config.MONGO_DB_AUTH_URL
    mongodb_client = MongoClient(uri)
    mongodb_client.drop_database('test')
    test_db = mongodb_client['test']
    fruits_collection = test_db['fruits']
    fruits_collection.insert_one({"banana": 10, "orange": 50})
    fruits_collection.insert_one({"banana": 15, "orange": 50})
    result_fruits = fruits_collection.find_one({"banana": 10})
    assert isinstance(result_fruits, dict)
    assert result_fruits["orange"] == 50
    assert result_fruits["banana"] == 10
