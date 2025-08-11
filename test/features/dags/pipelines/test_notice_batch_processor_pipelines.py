from typing import List

from pytest_bdd import given, when, then, scenario

from src.dags.pipelines.notice_batch_processor_pipelines import publish_notices_in_batch
from src.dags.pipelines.notice_processor_pipelines import notice_publish_pipeline
from src.dags.pipelines.pipeline_protocols import NoticePipelineOutput
from src.ted_sws.core.model.notice import Notice, NoticeStatus
from src.ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from test.mocks.mock_sftp_publisher import MockSFTPPublisherWithLimitedConnections


@scenario("test_notice_batch_processor_pipelines.feature",
          "Publishing fail on multiple connections using individual publishing but succeeds with batch publishing")
def test_dag_run_success_all_default_status():
    pass


@given("a list of 3 notices to be published")
def test_a_list_of_notices_to_be_published(dummy_list_of_3_notices_to_be_published: List[Notice]):
    assert dummy_list_of_3_notices_to_be_published is not None
    assert len(dummy_list_of_3_notices_to_be_published) == 3
    for notice in dummy_list_of_3_notices_to_be_published:
        assert notice is not None
        assert isinstance(notice, Notice)
        assert notice.status == NoticeStatus.ELIGIBLE_FOR_PUBLISHING


@when(name="publishing each notice individually in a sftp publisher with threshold of 2 notices",
      target_fixture="notices_result")
def test_publish_notices_individually(
        dummy_list_of_3_notices_to_be_published: List[Notice]
) -> List[NoticePipelineOutput]:
    mock_sftp_publisher = MockSFTPPublisherWithLimitedConnections(connection_threshold=2)
    notices_result: List[NoticePipelineOutput] = []
    for notice in dummy_list_of_3_notices_to_be_published:
        try:
            processed = notice_publish_pipeline(notice=notice,
                                                publisher=mock_sftp_publisher)
        except Exception:
            processed = NoticePipelineOutput(notice=notice, processed=False)
        notices_result.append(processed)
    return notices_result


@then("1 notice fail to publish due to connection limits")
def verify_failures(notices_result: List[NoticePipelineOutput]):
    published_count = sum(1 for notice_result in notices_result if notice_result.processed == True)
    failed_count = len(notices_result) - published_count

    assert failed_count == 1, f"Expected 1 failure, got {failed_count}"


@when(name="publishing the same notices in batch in a sftp publisher with threshold of 2 notices",
      target_fixture="notices_result")
def test_publish_notices_in_batch_mode(
        dummy_list_of_3_notices_to_be_published: List[Notice],
        mongodb_client,
) -> List[NoticePipelineOutput]:
    mock_sftp_publisher = MockSFTPPublisherWithLimitedConnections(connection_threshold=2)
    notice_repository = NoticeRepository(mongodb_client)
    notice_ids: List[str] = []
    for notice in dummy_list_of_3_notices_to_be_published:
        notice_repository.add(notice)
        notice_ids.append(notice.ted_id)

    return publish_notices_in_batch(notice_ids=notice_ids, mongodb_client=mongodb_client,
                                    sftp_publisher=mock_sftp_publisher)


@then("all notices are successfully published")
def verify_all_published(notices_result: List[NoticePipelineOutput]):
    all_published = all(notice_result.processed == True for notice_result in notices_result)

    assert all_published, "Not all notices were published"