from datetime import date

from ted_sws import config
from ted_sws.data_manager.adapters.daily_notices_metadata_repository import DailyNoticesMetadataRepository
from ted_sws.data_manager.services.daily_notices_metadata_services import update_daily_notices_metadata_from_ted
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI


def test_update_daily_notices_metadata_from_ted(mongodb_client):
    """
    Test update_daily_notices_metadata_from_ted function
    """

    ted_api = TedAPIAdapter(TedRequestAPI(), config.TED_API_URL)
    daily_notices_metadata_repo = DailyNoticesMetadataRepository(mongodb_client)

    update_daily_notices_metadata_from_ted(start_date=date(2021, 1, 7),
                                           end_date=date(2021, 1, 7),
                                           ted_api=ted_api,
                                           mongo_client=mongodb_client,
                                           daily_notices_metadata_repo=daily_notices_metadata_repo)

    # update_daily_notices_metadata_from_ted(start_date=date(2021, 1, 7),
    #                                        end_date=date(2021, 1, 7),
    #                                        ted_api=ted_api,
    #                                        mongo_client=mongodb_client,
    #                                        daily_notices_metadata_repo=daily_notices_metadata_repo)