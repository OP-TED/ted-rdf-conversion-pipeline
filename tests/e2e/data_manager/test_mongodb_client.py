import string
import random

from pymongo import MongoClient
from pymongo.command_cursor import CommandCursor

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


def random_string() -> str:
    return ''.join(random.choice(string.ascii_letters) for i in range(random.randint(5, 30)))


def random_list() -> list:
    return [random.randint(5, 30) for i in range(0, random.randint(3, 10))]


def random_object() -> dict:
    return {"xpath": random_list(),
            "notices": random.randint(0, 1000)}


pipeline = [
    {
        "$project": {
            "notices": 1,
            "_id": 0
        }
    }
]


def test_mongodb_queries():
    uri = config.MONGO_DB_AUTH_URL
    mongodb_client = MongoClient(uri)
    mongodb_client.drop_database('test')
    test_db = mongodb_client['test']
    objects_collection = test_db['objects']
    print(type(objects_collection))
    for i in range(0, 20):
        objects_collection.insert_one(random_object())

    unique_xpaths = objects_collection.distinct("xpath")
    print(type(unique_xpaths))

    unique_notice_ids = objects_collection.distinct("notices")
    print("unique_notice_ids: ", unique_notice_ids)
    print("unique_xpaths: ", unique_xpaths)
    minimal_set_of_xpaths = []
    covered_notice_ids = []
    while len(unique_notice_ids):
        xpaths = []
        for xpath_id in list(unique_xpaths):
            tmp_result = list(
                objects_collection.aggregate([{"$match": {"xpath": {"$in": [xpath_id]},
                                                          "notices": {"$in": unique_notice_ids}}},
                                              {"$project": {"_id": 0,
                                                            "notice_id": "$notices"}},
                                              {

                                                  "$group": {"_id": None,
                                                             "notice_ids": {"$push": "$notice_id"}
                                                             }
                                              },
                                              {"$project": {"_id": 0,
                                                            "notice_ids": 1,
                                                            "count_notices": {"$size": "$notice_ids"}}},
                                              {
                                                  "$addFields": {"xpath": xpath_id}
                                              }
                                              ]))

            if len(tmp_result):
                xpaths.append(tmp_result[0])

        # for xpath in xpaths:
        #  print(xpath)
        top_xpath = sorted(xpaths, key=lambda d: d['count_notices'], reverse=True)[0]
        minimal_set_of_xpaths.append(top_xpath["xpath"])
        notice_ids = top_xpath["notice_ids"]
        for notice_id in notice_ids:
            if notice_id in unique_notice_ids:
                unique_notice_ids.remove(notice_id)
            covered_notice_ids.append(notice_id)

    print("minimal_set_of_xpaths: ", minimal_set_of_xpaths)
    print("covered_notice_ids: ", covered_notice_ids)


def test_mongo_db_query_2():
    uri = config.MONGO_DB_AUTH_URL
    mongodb_client = MongoClient(uri)
    mongodb_client.drop_database('test')
    test_db = mongodb_client['test']
    objects_collection = test_db['objects']
    print(type(objects_collection))
    for i in range(0, 3):
        objects_collection.insert_one(random_object())

    unique_xpaths = objects_collection.distinct("xpath")
    print(type(unique_xpaths))

    unique_notice_ids = objects_collection.distinct("notices")
    print("unique_notice_ids: ", unique_notice_ids)
    print("unique_xpaths: ", unique_xpaths)
    result = objects_collection.aggregate([
        {
            "$group": {"_id": None,
                       "xpaths": {"$push": "$xpath"}
                       }
        },
        # {"$project": {"_id": 0,
        #               "xpaths": 1,
        #               }},
        {
            "$project": {
                "_id": 0,
                "xpaths": {
                    "$setUnion": {
                        "$reduce": {
                            "input": '$xpaths',
                            "initialValue": [],
                            "in": {"$concatArrays": ['$$value', '$$this']}
                        }
                    }
                }
            }
        }
    ])
    for r in result:
        print(r)
