import pytest

from ted_sws.domain.model.notice import NoticeStatus
from ted_sws.metadata_normaliser.services.metadata_normalizer import normalise_notice, normalise_notice_by_id, \
    MetadataNormaliser


def test_metadata_normaliser_by_notice(raw_notice):
    notice = normalise_notice(raw_notice)
    assert notice.normalised_metadata
    assert notice.normalised_metadata.title
    assert notice.status == NoticeStatus.NORMALISED_METADATA


def test_metadata_normaliser_by_notice_id(notice_id, notice_repository, notice_2018):
    notice_repository.add(notice_2018)
    with pytest.raises(AttributeError):
        notice = normalise_notice_by_id(notice_id=notice_2018.ted_id, notice_repository=notice_repository)
        assert notice.normalised_metadata
        assert notice.normalised_metadata.title
        assert notice.status == NoticeStatus.NORMALISED_METADATA


def test_metadata_normaliser_by_wrong_notice_id(notice_repository):
    notice_id = "wrong-notice-id"
    with pytest.raises(ValueError):
        normalise_notice_by_id(notice_id=notice_id, notice_repository=notice_repository)


def test_metadata_normaliser(raw_notice):
    notice = raw_notice
    MetadataNormaliser(notice=notice).normalise_metadata()

    assert notice.normalised_metadata
    assert notice.normalised_metadata.title
    assert notice.status == NoticeStatus.NORMALISED_METADATA
