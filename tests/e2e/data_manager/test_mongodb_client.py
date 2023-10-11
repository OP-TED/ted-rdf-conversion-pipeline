from ted_sws import config
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_manager.services.create_batch_collection_materialised_view import \
    create_batch_collection_materialised_view, NOTICE_PROCESS_BATCH_COLLECTION_NAME
from ted_sws.data_manager.services.create_notice_collection_materialised_view import \
    create_notice_collection_materialised_view, NOTICES_MATERIALISED_VIEW_NAME, create_notice_kpi_collection, \
    NOTICE_KPI_COLLECTION_NAME
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice
from ted_sws.event_manager.adapters.event_handler_config import DAGLoggerConfig
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.model.event_message import NoticeEventMessage
from ted_sws.event_manager.services.logger_from_context import get_env_logger
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher
from ted_sws.notice_metadata_processor.services.metadata_normalizer import normalise_notice


def test_create_materialised_view_for_notices(mongodb_client):
    notice_id = "696661-2022"
    ted_api_query = {"q": f"ND=[{notice_id}]"}
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    NoticeFetcher(notice_repository=notice_repository,
                  ted_api_adapter=TedAPIAdapter(
                      request_api=TedRequestAPI())).fetch_notices_by_query(query=ted_api_query)
    logger = get_env_logger(EventLogger(DAGLoggerConfig(mongodb_client=mongodb_client)))
    notice_event = NoticeEventMessage(notice_id=notice_id, domain_action="test")
    notice_event.caller_name = "execute"
    notice_event.start_record()
    notice = notice_repository.get(reference=notice_id)
    indexed_notice = index_notice(notice=notice)
    normalised_notice = normalise_notice(notice=indexed_notice)
    notice = normalised_notice
    notice_repository.update(notice=normalised_notice)
    notice_event.end_record()
    notice_event.notice_form_number = notice.normalised_metadata.form_number
    notice_event.notice_eforms_subtype = notice.normalised_metadata.eforms_subtype
    notice_event.notice_status = str(notice.status)
    logger.info(event_message=notice_event)
    create_notice_collection_materialised_view(mongo_client=mongodb_client)
    db = mongodb_client[config.MONGO_DB_AGGREGATES_DATABASE_NAME]
    assert NOTICES_MATERIALISED_VIEW_NAME in db.list_collection_names()
    document = db[NOTICES_MATERIALISED_VIEW_NAME].find_one()
    assert document is not None
    fields_in_the_materialised_view = document.keys()
    assert 'form_type' in fields_in_the_materialised_view
    assert 'form_number' in fields_in_the_materialised_view
    assert 'eforms_subtype' in fields_in_the_materialised_view
    assert 'eu_institution' in fields_in_the_materialised_view
    assert 'extracted_legal_basis_directive' in fields_in_the_materialised_view
    assert 'legal_basis_directive' in fields_in_the_materialised_view
    assert 'ojs_type' in fields_in_the_materialised_view
    assert 'country_of_buyer' in fields_in_the_materialised_view
    assert 'notice_type' in fields_in_the_materialised_view
    assert 'xsd_version' in fields_in_the_materialised_view
    assert 'publication_date' in fields_in_the_materialised_view

    create_notice_kpi_collection(mongo_client=mongodb_client)
    if NOTICE_KPI_COLLECTION_NAME in db.list_collection_names():
        document = db[NOTICE_KPI_COLLECTION_NAME].find_one()
        assert document is not None
        fields_in_the_kpi_collection = document.keys()
        assert 'exec_time' in fields_in_the_kpi_collection
        assert 'form_number' in fields_in_the_kpi_collection
        assert 'eforms_subtype' in fields_in_the_kpi_collection
        assert 'status' in fields_in_the_kpi_collection


def test_create_materialised_view_for_batches(mongodb_client):
    create_batch_collection_materialised_view(mongo_client=mongodb_client)
    #TODO: rewrite this test
    # Current implementation is dependent on the data in the database,
    # dependence is from another tests that provide this data.
    # Now mongodb_client is mocked, so there is no data in the database.
    # db = mongodb_client[config.MONGO_DB_AGGREGATES_DATABASE_NAME]
    # assert NOTICE_PROCESS_BATCH_COLLECTION_NAME in db.list_collection_names()
    # document = db[NOTICE_PROCESS_BATCH_COLLECTION_NAME].find_one()
    # if document is not None:
    #     fields_in_the_materialised_view = document.keys()
    #     assert 'exec_time' in fields_in_the_materialised_view
    #     assert 'nr_of_pipelines' in fields_in_the_materialised_view
    #     assert 'batch_nr_of_notices' in fields_in_the_materialised_view
