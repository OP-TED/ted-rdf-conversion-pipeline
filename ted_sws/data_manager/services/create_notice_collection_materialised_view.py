from pymongo import MongoClient, ASCENDING, DESCENDING

from ted_sws import config
from ted_sws.data_manager.services import MONGO_DB_AGGREGATES_DATABASE_DEFAULT_NAME

NOTICE_COLLECTION_NAME = "notice_collection"
NOTICES_MATERIALISED_VIEW_NAME = "notices_collection_materialised_view"
NOTICE_EVENTS_COLLECTION_NAME = "notice_events"
NOTICE_KPI_COLLECTION_NAME = "notice_kpi"


def create_notice_collection_materialised_view(mongo_client: MongoClient):
    """
    Creates a collection with materialized view used on metabase by aggregating notices collection.
    :param mongo_client: MongoDB client to connect
    """
    database = mongo_client[config.MONGO_DB_AGGREGATES_DATABASE_NAME or MONGO_DB_AGGREGATES_DATABASE_DEFAULT_NAME]
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
            "$out": NOTICES_MATERIALISED_VIEW_NAME
        }
    ])
    materialised_view = database[NOTICES_MATERIALISED_VIEW_NAME]
    materialised_view.create_index([("created_at", DESCENDING)])
    materialised_view.create_index([("publication_date", DESCENDING)])
    materialised_view.create_index([("eu_institution", ASCENDING)])
    materialised_view.create_index([("status", ASCENDING)])
    materialised_view.create_index([("form_number", ASCENDING)])
    materialised_view.create_index([("form_number", ASCENDING), ("status", ASCENDING)])
    materialised_view.create_index([("execution_time", ASCENDING)])


def create_notice_kpi_collection(mongo_client: MongoClient):
    """
    Creates a collection with kpi for existing notices.
    :param mongo_client: MongoDB client to connect
    """
    database = mongo_client[config.MONGO_DB_AGGREGATES_DATABASE_NAME or MONGO_DB_AGGREGATES_DATABASE_DEFAULT_NAME]
    notice_events_collection = database[NOTICE_EVENTS_COLLECTION_NAME]
    notice_events_collection.aggregate([
        {
            "$match": {
                "caller_name": "execute",
            }
        },
        {
            "$group": {
                "_id": "$notice_id",
                "exec_time": {"$sum": "$duration"},
                "form_number": {"$first": "$notice_form_number"},
                "eforms_subtype": {"$first": "$notice_eforms_subtype"}
            }
        },
        {
            "$out": NOTICE_KPI_COLLECTION_NAME
        }
    ])
