from ted_sws.domain.model.notice import NoticeStatus
from ted_sws.metadata_normaliser.services.metadata_normalizer import MetadataNormaliser


def test_metadata_extractor(raw_notice):
    notice = raw_notice
    MetadataNormaliser(notice=notice).normalise_metadata()


    assert notice.normalised_metadata
    assert notice.status == NoticeStatus.NORMALISED_METADATA