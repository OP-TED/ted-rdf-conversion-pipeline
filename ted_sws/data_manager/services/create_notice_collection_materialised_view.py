from pymongo import MongoClient, ASCENDING, DESCENDING

from ted_sws import config

NOTICE_COLLECTION_NAME = "notice_collection"
NOTICES_MATERIALISED_VIEW_NAME = "notices_collection_materialised_view"
NOTICE_EVENTS_COLLECTION_NAME = "notice_events"
NOTICE_PROCESS_BATCH_COLLECTION_NAME = "batch_events"
LOG_EVENTS_COLLECTION_NAME = "log_events"


def create_notice_collection_materialised_view(mongo_client: MongoClient):
    database = mongo_client[config.MONGO_DB_AGGREGATES_DATABASE_NAME or "aggregates_db"]
    notice_collection = database[NOTICE_COLLECTION_NAME]
    notice_collection.aggregate([
        {
            "$project": {
                "_id": True,
                "created_at": True,
                "status": True,
                "validation_summary": True,
                "version_number": True,
                "form_number": "$normalised_metadata.form_number",
                "form_type": "$normalised_metadata.form_type",
                "eu_institution": "$normalised_metadata.eu_institution",
                "extracted_legal_basis_directive": "$normalised_metadata.extracted_legal_basis_directive",
                "ojs_type": "$normalised_metadata.ojs_type",
                "legal_basis_directive": "$normalised_metadata.legal_basis_directive",
                "country_of_buyer": "$normalised_metadata.country_of_buyer",
                "eforms_subtype": "$normalised_metadata.eforms_subtype",
                "notice_type": "$normalised_metadata.notice_type",
                "xsd_version": "$normalised_metadata.xsd_version",
                "publication_date": "$normalised_metadata.publication_date",
            }
        },
        {
            "$lookup":
                {
                    "from": f"{NOTICE_EVENTS_COLLECTION_NAME}",
                    "localField": "_id",
                    "foreignField": "notice_id",
                    "as": "notice_logs",
                    "pipeline": [
                        {
                            "$group": {
                                "_id": "$notice_id",
                                "exec_time": {"$sum": "$duration"}
                            }
                        }
                    ]
                },
        },
        {"$unwind": '$notice_logs'},
        {
            "$merge": {
                "into": NOTICES_MATERIALISED_VIEW_NAME
            }
        }
    ])
    materialised_view = database[NOTICES_MATERIALISED_VIEW_NAME]
    materialised_view.create_index([("created_at", DESCENDING)])
    materialised_view.create_index([("publication_date", DESCENDING)])
    materialised_view.create_index([("eu_institution", ASCENDING)])
    materialised_view.create_index([("status", ASCENDING)])
    materialised_view.create_index([("form_number", ASCENDING)])
    materialised_view.create_index([("form_number", ASCENDING), ("status", ASCENDING)])
    materialised_view.create_index([("form_number", ASCENDING), ("legal_basis_directive", ASCENDING)])

    batch_collection = database[LOG_EVENTS_COLLECTION_NAME]
    batch_collection.aggregate([
        {
            "$group": {
                "_id": {"process_id": "$metadata.process_id",
                        "nr_of_notices": "$kwargs.number_of_notices",
                        "caller_name": "execute"
                        },
                "exec_time": {"$sum": "$duration"},
                "nr_of_pipelines": {"$sum": 1}
            }
        },
        {
            "$merge": {
                "into": NOTICE_PROCESS_BATCH_COLLECTION_NAME
            }
        }
    ])
