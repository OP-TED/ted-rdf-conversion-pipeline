from pymongo import MongoClient
from ted_sws import config
import psycopg2
from psycopg2 import Error

DAG_COLLECTION_NAME = "dag_events"

POSTGRES_HOST = "host.docker.internal"
POSTGRES_PORT = "5432"


def _request_data_from_posgres():
    execution_time_query = """
    SELECT exec_time.dag_id,
           round(min(exec_time.exec_seconds)::numeric, 2) as min,
           round(avg(exec_time.exec_seconds)::numeric, 2) as avg,
           round(max(exec_time.exec_seconds)::numeric, 2) as max
    FROM
        (select dag_id,
                extract('epoch' from (end_date - start_date)) as exec_seconds
         from public.dag_run
         where state like 'success') exec_time
    group by dag_id
    """

    connection = psycopg2.connect(user=config.AIRFLOW_POSTGRES_USER,
                                  password=config.AIRFLOW_POSTGRES_PASSWORD,
                                  host=POSTGRES_HOST,
                                  port=POSTGRES_PORT,
                                  database=config.AIRFLOW_POSTGRES_DB_NAME)
    cursor = connection.cursor()
    cursor.execute(execution_time_query)
    query_result = cursor.fetchall()
    cursor.close()
    connection.close()

    return query_result


def create_dag_collection_materialised_view(mongo_client: MongoClient):
    database = mongo_client[config.MONGO_DB_AGGREGATES_DATABASE_NAME or "aggregates_db"]
    dag_collection = database[DAG_COLLECTION_NAME]

    dag_query_result = _request_data_from_posgres()
    if dag_query_result:
        for row in dag_query_result:
            dag_id, min_t, avg_t, max_t = row
            doc = {
                "dag_id": dag_id,
                "min_exec_time": float(min_t),
                "avg_exec_time": float(avg_t),
                "max_exec_time": float(max_t)
            }
            dag_collection.replace_one({"dag_id": doc["dag_id"]}, doc, upsert=True)
