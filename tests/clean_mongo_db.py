from pymongo import MongoClient

from ted_sws import config
from logging import getLogger

logger = getLogger(__name__)

def clean_mongo_db():
    uri = config.MONGO_DB_AUTH_URL
    if "staging" in uri:
        mongodb_client = MongoClient(uri)
        protected_databases = ['admin', 'config', 'local']
        existing_databases = mongodb_client.list_database_names()
        databases_to_delete = list(set(existing_databases) - set(protected_databases))

        for database in databases_to_delete:
            mongodb_client.drop_database(database)
    else:
        logger.warning("This was an attempt to erase the DB in NON-Staging environment.")

clean_mongo_db()
