from datetime import datetime, timedelta

from airflow import Dataset

DEFAULT_DAG_ARGUMENTS = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2022, 1, 1),
    "email": ["info@meaningfy.ws"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=3600),
    "max_active_runs": 15,
    "concurrency": 15,
    "execution_timeout": timedelta(days=10),
}

NOTICE_NORMALISATION_PIPELINE_TASK_ID = "notice_normalisation_pipeline"
NOTICE_TRANSFORMATION_PIPELINE_TASK_ID = "notice_transformation_pipeline"
NOTICE_DISTILLATION_PIPELINE_TASK_ID = "notice_distillation_pipeline"
NOTICE_VALIDATION_PIPELINE_TASK_ID = "notice_validation_pipeline"
NOTICE_PACKAGE_PIPELINE_TASK_ID = "notice_package_pipeline"
NOTICE_PUBLISH_PIPELINE_TASK_ID = "notice_publish_pipeline"
STOP_PROCESSING_TASK_ID = "stop_processing"
BRANCH_SELECTOR_TASK_ID = 'branch_selector'
SELECTOR_BRANCH_BEFORE_TRANSFORMATION_TASK_ID = "switch_to_transformation"
SELECTOR_BRANCH_BEFORE_VALIDATION_TASK_ID = "switch_to_validation"
SELECTOR_BRANCH_BEFORE_PACKAGE_TASK_ID = "switch_to_package"
SELECTOR_BRANCH_BEFORE_PUBLISH_TASK_ID = "switch_to_publish"

BRANCH_SELECTOR_MAP = {NOTICE_NORMALISATION_PIPELINE_TASK_ID: NOTICE_NORMALISATION_PIPELINE_TASK_ID,
                       NOTICE_TRANSFORMATION_PIPELINE_TASK_ID: SELECTOR_BRANCH_BEFORE_TRANSFORMATION_TASK_ID,
                       NOTICE_VALIDATION_PIPELINE_TASK_ID: SELECTOR_BRANCH_BEFORE_VALIDATION_TASK_ID,
                       NOTICE_PACKAGE_PIPELINE_TASK_ID: SELECTOR_BRANCH_BEFORE_PACKAGE_TASK_ID,
                       NOTICE_PUBLISH_PIPELINE_TASK_ID: SELECTOR_BRANCH_BEFORE_PUBLISH_TASK_ID
                       }

# This is a formal name, not an actual connection string.
NOTICES_COLLECTION_DATASET: Dataset = Dataset("db://aggregates_db/notices_collection")
MATERIALISED_VIEW_DATASET: Dataset = Dataset("db://aggregates_db/notices_collection_materialised_view")
