from unittest.mock import patch

import pymongo

from src.dags.operators.DagBatchPipelineOperator import NoticeBatchPipelineOperator, NOTICE_IDS_KEY, \
    NOTICES_WITH_STATUS_KEY
from src.ted_sws.core.model.notice import Notice


@patch("src.dags.operators.DagBatchPipelineOperator.smart_xcom_push")
@patch("src.dags.operators.DagBatchPipelineOperator.smart_xcom_pull")
@patch("src.dags.operators.DagBatchPipelineOperator.MongoClient")
def test_notice_batch_pipeline_operator_soft_fail(
        mock_mongo_client,
        mock_xcom_pull,
        mock_xcom_push,
        mongodb_client: pymongo.MongoClient,
):
    mock_mongo_client.return_value = mongodb_client
    mock_xcom_pull.side_effect = lambda key, **kwargs: {
        NOTICE_IDS_KEY: ["notice_2021"],
        NOTICES_WITH_STATUS_KEY: {"notice_2021": "RAW"},
    }.get(key)
    mock_xcom_push.side_effect = None

    def pipeline_callable_that_raises_exception(_notice: Notice, _mongodb_client: pymongo.MongoClient):
        raise Exception

    operator = NoticeBatchPipelineOperator(
        task_id="dummy_task_id_string",
        notice_pipeline_callable=pipeline_callable_that_raises_exception,
    )

    operator.execute(context=None)
