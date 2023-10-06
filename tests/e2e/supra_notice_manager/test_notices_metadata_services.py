from ted_sws import config
from ted_sws.core.model.supra_notice import DailyNoticesMetadata
from ted_sws.data_manager.adapters.daily_notices_metadata_repository import DailyNoticesMetadataRepository
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI
from ted_sws.supra_notice_manager.services.daily_notices_metadata_services import \
    update_daily_notices_metadata_from_ted, \
    update_daily_notices_metadata_with_fetched_data


def test_update_daily_notices_metadata_from_ted(fake_mongodb_client, example_date, example_date_without_notices):
    """
    Test update_daily_notices_metadata_from_ted function
    """

    ted_api = TedAPIAdapter(TedRequestAPI(), config.TED_API_URL)
    daily_notices_metadata_repo = DailyNoticesMetadataRepository(fake_mongodb_client)

    update_daily_notices_metadata_from_ted(start_date=example_date_without_notices,
                                           end_date=example_date_without_notices,
                                           ted_api=ted_api,
                                           daily_notices_metadata_repo=daily_notices_metadata_repo)

    assert len(list(daily_notices_metadata_repo.list())) == 1

    update_daily_notices_metadata_from_ted(start_date=example_date,
                                           end_date=example_date,
                                           ted_api=ted_api,
                                           daily_notices_metadata_repo=daily_notices_metadata_repo)

    daily_notices_metadata: DailyNoticesMetadata = daily_notices_metadata_repo.get(example_date)
    assert daily_notices_metadata is not None
    assert daily_notices_metadata.ted_api_notice_ids is not None
    assert len(daily_notices_metadata.ted_api_notice_ids) == daily_notices_metadata.ted_api_notice_count

    update_daily_notices_metadata_from_ted(start_date=example_date,
                                           end_date=example_date,
                                           ted_api=ted_api,
                                           daily_notices_metadata_repo=daily_notices_metadata_repo)

    assert len(list(daily_notices_metadata_repo.list())) == 2


def test_update_daily_notices_metadata_with_fetched_data(fake_mongodb_client,
                                                         fake_notice_repository,
                                                         example_date,
                                                         notice_with_rdf_manifestation,
                                                         notice_2021):
    daily_notices_metadata_repo = DailyNoticesMetadataRepository(fake_mongodb_client)

    update_daily_notices_metadata_with_fetched_data(start_date=example_date,
                                                    end_date=example_date,
                                                    notice_repo=fake_notice_repository,
                                                    daily_notices_metadata_repo=daily_notices_metadata_repo)

    assert daily_notices_metadata_repo.get(example_date) is None

    fake_notice_repository.add(notice_with_rdf_manifestation)
    fake_notice_repository.add(notice_2021)

    daily_notices_metadata: DailyNoticesMetadata = DailyNoticesMetadata(aggregation_date=example_date)
    daily_notices_metadata.ted_api_notice_ids.append(notice_with_rdf_manifestation.ted_id)
    daily_notices_metadata.ted_api_notice_ids.append(notice_2021.ted_id)
    daily_notices_metadata_repo.add(daily_notices_metadata)

    update_daily_notices_metadata_with_fetched_data(start_date=example_date,
                                                    end_date=example_date,
                                                    notice_repo=fake_notice_repository,
                                                    daily_notices_metadata_repo=daily_notices_metadata_repo)

    daily_notices_metadata: DailyNoticesMetadata = daily_notices_metadata_repo.get(example_date)

    assert daily_notices_metadata is not None

    assert daily_notices_metadata.fetched_notices_count == 2
    assert daily_notices_metadata.ted_api_notice_count == 2
    assert daily_notices_metadata.notice_statuses['RAW'] == 2
    assert daily_notices_metadata.notice_statuses['INDEXED'] > 0
    assert daily_notices_metadata.notice_statuses['NORMALISED_METADATA'] > 0
    assert daily_notices_metadata.notice_statuses['ELIGIBLE_FOR_TRANSFORMATION'] > 0
    assert daily_notices_metadata.notice_statuses['INELIGIBLE_FOR_TRANSFORMATION'] == 0

    assert daily_notices_metadata.notice_statuses_coverage['RAW_coverage'] == 1.0
    assert daily_notices_metadata.notice_statuses_coverage['INDEXED_coverage'] == 0.5
    assert daily_notices_metadata.notice_statuses_coverage['NORMALISED_METADATA_coverage'] == 0.5
    assert daily_notices_metadata.notice_statuses_coverage['INELIGIBLE_FOR_TRANSFORMATION_coverage'] == 0.0
    assert len(daily_notices_metadata.mapping_suite_packages) > 0
