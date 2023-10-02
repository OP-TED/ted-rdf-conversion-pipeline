from ted_sws.data_manager.adapters.daily_notices_metadata_repository import DailyNoticesMetadataRepository


def test_daily_notices_metadata_repository(mongodb_client, daily_notices_metadata):
    daily_notices_metadata_repository = DailyNoticesMetadataRepository(mongodb_client=mongodb_client)

    # Upset is False by default
    daily_notices_metadata_repository.update(daily_notices_metadata)
    assert daily_notices_metadata_repository.get(daily_notices_metadata.aggregation_date) is None

    # Creates a new object
    daily_notices_metadata_repository.add(daily_notices_metadata)
    assert daily_notices_metadata == daily_notices_metadata_repository.get(daily_notices_metadata.aggregation_date)

    # Check if only on object in the repository
    assert len(list(daily_notices_metadata_repository.list())) == 1

    # Only one object in the repository
    assert list(daily_notices_metadata_repository.list()) == [daily_notices_metadata]

    # Check if on add updates the object
    daily_notices_metadata_repository.add(daily_notices_metadata)
    assert list(daily_notices_metadata_repository.list()) == [daily_notices_metadata]
