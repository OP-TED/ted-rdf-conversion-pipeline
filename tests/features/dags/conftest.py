from unittest.mock import Mock

import pytest

from dags.operators.DagBatchPipelineOperator import NoticeBatchPipelineOperator
from dags.pipelines.notice_processor_pipelines import notice_normalisation_pipeline
from ted_sws.core.model.notice import NoticeStatus
from tests.fakes.fake_dag_context import FakeDAGContext


@pytest.fixture
def mock_mongodb_client():
    """Mock MongoDB client"""
    return Mock()


@pytest.fixture
def mock_dag_context():
    """Mock DAG context"""
    return FakeDAGContext()


@pytest.fixture
def batch_pipeline_operator():
    """Create a batch pipeline operator for testing"""
    return NoticeBatchPipelineOperator(
        task_id="test_batch_operator",
        notice_pipeline_callable=notice_normalisation_pipeline,
        notice_success_statuses=[NoticeStatus.PUBLISHED, NoticeStatus.PUBLICLY_AVAILABLE]
    )
