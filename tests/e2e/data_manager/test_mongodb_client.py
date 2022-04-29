from pymongo import MongoClient

from ted_sws import config
import gridfs


def test_mongodb_client(notice_2016):
    print(notice_2016.xml_manifestation)
    uri = config.MONGO_DB_AUTH_URL
    mongodb_client = MongoClient(uri)
    mongodb_client.drop_database('test')
    test_db = mongodb_client['test']
    fs = gridfs.GridFS(test_db)
    key = None
    for i in range(0,10):
        key = fs.put(data="Hello my name is Stefan!".encode("utf-8"))
        print("key is :",key)
    result_data = fs.get(key).read().decode("utf-8")
    print("result data:", result_data)
    fruits_collection = test_db['fruits']
    fruits_collection.insert_one({"banana": 10, "orange": 50})
    fruits_collection.insert_one({"banana": 15, "orange": 50})
    result_fruits = fruits_collection.find_one({"banana": 10})
    assert isinstance(result_fruits, dict)
    assert result_fruits["orange"] == 50
    assert result_fruits["banana"] == 10
