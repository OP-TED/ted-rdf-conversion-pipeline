from unittest.mock import patch

import pytest

from src.ted_sws.core.model.notice import NoticeStatus
from src.ted_sws.data_manager.adapters.notice_repository import NoticeRepository, NOTICE_TED_ID, NOTICE_STATUS
from src.ted_sws.data_manager.services.notice_batch_service import (
    group_notice_ids_by_reprocess_status,
    group_notice_ids_by_status,
)


def test_group_notice_ids_by_status_empty_list(mongodb_client, aggregates_database_name):
    result = group_notice_ids_by_status([], mongodb_client=mongodb_client)
    assert result == []


def test_group_notice_ids_by_status_single_notice_with_valid_status(mongodb_client, aggregates_database_name):
    mongodb_client.drop_database(aggregates_database_name)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_repository.collection.insert_one({
        NOTICE_TED_ID: "123456-2022",
        NOTICE_STATUS: "RAW"
    })

    result = group_notice_ids_by_status(["123456-2022"], mongodb_client=mongodb_client)

    assert len(result) == 1
    assert result[0].notice_status == NoticeStatus.RAW
    assert result[0].notice_ids == ["123456-2022"]
    assert result[0].start_with_step_name == "notice_normalisation_pipeline"


def test_group_notice_ids_by_status_multiple_notices_same_status(mongodb_client, aggregates_database_name):
    mongodb_client.drop_database(aggregates_database_name)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_repository.collection.insert_many([
        {NOTICE_TED_ID: "123456-2022", NOTICE_STATUS: "RAW"},
        {NOTICE_TED_ID: "234567-2022", NOTICE_STATUS: "RAW"},
        {NOTICE_TED_ID: "345678-2022", NOTICE_STATUS: "RAW"},
    ])

    result = group_notice_ids_by_status(
        ["123456-2022", "234567-2022", "345678-2022"],
        mongodb_client=mongodb_client
    )

    assert len(result) == 1
    assert result[0].notice_status == NoticeStatus.RAW
    assert set(result[0].notice_ids) == {"123456-2022", "234567-2022", "345678-2022"}


def test_group_notice_ids_by_status_multiple_notices_different_statuses(mongodb_client, aggregates_database_name):
    mongodb_client.drop_database(aggregates_database_name)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_repository.collection.insert_many([
        {NOTICE_TED_ID: "123456-2022", NOTICE_STATUS: "RAW"},
        {NOTICE_TED_ID: "234567-2022", NOTICE_STATUS: "DISTILLED"},
        {NOTICE_TED_ID: "345678-2022", NOTICE_STATUS: "PACKAGED"},
    ])

    result = group_notice_ids_by_status(
        ["123456-2022", "234567-2022", "345678-2022"],
        mongodb_client=mongodb_client
    )

    assert len(result) == 3
    statuses = {batch.notice_status for batch in result}
    assert statuses == {NoticeStatus.RAW, NoticeStatus.DISTILLED, NoticeStatus.PACKAGED}


def test_group_notice_ids_by_status_unknown_status_not_in_mapping(mongodb_client, aggregates_database_name):
    mongodb_client.drop_database(aggregates_database_name)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_repository.collection.insert_one({
        NOTICE_TED_ID: "123456-2022",
        NOTICE_STATUS: "UNKNOWN_STATUS"
    })

    with pytest.raises(KeyError):
        group_notice_ids_by_status(["123456-2022"], mongodb_client=mongodb_client)


def test_group_notice_ids_by_status_notice_without_status(mongodb_client, aggregates_database_name):
    mongodb_client.drop_database(aggregates_database_name)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_repository.collection.insert_one({
        NOTICE_TED_ID: "123456-2022",
    })

    result = group_notice_ids_by_status(["123456-2022"], mongodb_client=mongodb_client)

    assert result == []


def test_group_notice_ids_by_status_notice_ids_not_found(mongodb_client, aggregates_database_name):
    mongodb_client.drop_database(aggregates_database_name)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_repository.collection.insert_one({
        NOTICE_TED_ID: "123456-2022",
        NOTICE_STATUS: "RAW"
    })

    result = group_notice_ids_by_status(["999999-2022"], mongodb_client=mongodb_client)

    assert result == []


@patch("src.ted_sws.data_manager.services.notice_batch_service.notice_ids_selector_by_status")
def test_group_notice_ids_by_reprocess_status_invalid_status(mock_selector):
    result = group_notice_ids_by_reprocess_status("InvalidStatus")

    assert result == []
    mock_selector.assert_not_called()


@patch("src.ted_sws.data_manager.services.notice_batch_service.notice_ids_selector_by_status")
def test_group_notice_ids_by_reprocess_status_valid_with_notices(mock_selector):
    mock_selector.return_value = ["123456-2022", "234567-2022"]

    result = group_notice_ids_by_reprocess_status("Unvalidated")

    assert len(result) == 1
    assert result[0].notice_status == NoticeStatus.DISTILLED
    assert result[0].notice_ids == ["123456-2022", "234567-2022"]
    assert result[0].start_with_step_name == "notice_validation_pipeline"


@patch("src.ted_sws.data_manager.services.notice_batch_service.notice_ids_selector_by_status")
def test_group_notice_ids_by_reprocess_status_valid_no_notices(mock_selector):
    mock_selector.return_value = []

    result = group_notice_ids_by_reprocess_status("Unvalidated")

    assert result == []


@patch("src.ted_sws.data_manager.services.notice_batch_service.notice_ids_selector_by_status")
def test_group_notice_ids_by_reprocess_status_with_dates(mock_selector):
    mock_selector.return_value = ["123456-2022"]

    result = group_notice_ids_by_reprocess_status(
        "Unvalidated",
        start_date="2022-01-01",
        end_date="2022-12-31"
    )

    assert len(result) == 1
    mock_selector.assert_called_once()
    call_kwargs = mock_selector.call_args.kwargs
    assert call_kwargs["start_date"] == "2022-01-01"
    assert call_kwargs["end_date"] == "2022-12-31"


@patch("src.ted_sws.data_manager.services.notice_batch_service.notice_ids_selector_by_status")
def test_group_notice_ids_by_reprocess_status_unnormalised(mock_selector):
    mock_selector.return_value = ["123456-2022"]

    result = group_notice_ids_by_reprocess_status("Unnormalised")

    assert len(result) == 1
    assert result[0].notice_status == NoticeStatus.RAW
    assert result[0].start_with_step_name == "notice_normalisation_pipeline"


@patch("src.ted_sws.data_manager.services.notice_batch_service.notice_ids_selector_by_status")
def test_group_notice_ids_by_reprocess_status_unpublished(mock_selector):
    mock_selector.return_value = ["123456-2022"]

    result = group_notice_ids_by_reprocess_status("Unpublished")

    assert len(result) == 1
    assert result[0].start_with_step_name == "notice_publish_pipeline"


@patch("src.ted_sws.data_manager.services.notice_batch_service.notice_ids_selector_by_status")
def test_group_notice_ids_by_reprocess_status_unpackaged(mock_selector):
    mock_selector.return_value = ["123456-2022"]

    result = group_notice_ids_by_reprocess_status("Unpackaged")

    assert len(result) == 1
    assert result[0].start_with_step_name == "notice_package_pipeline"
