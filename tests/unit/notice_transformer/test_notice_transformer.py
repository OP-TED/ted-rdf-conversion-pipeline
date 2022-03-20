from ted_sws.domain.model.notice import NoticeStatus
from ted_sws.notice_transformer.services.notice_transformer import NoticeTransformer


def test_notice_transformer(fake_rml_mapper, fake_mapping_suite, notice_2018):
    notice_transformer = NoticeTransformer(mapping_suite=fake_mapping_suite, rml_mapper=fake_rml_mapper)
    notice_2018._status = NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION
    notice_transformer.transform_notice(notice = notice_2018)
    assert notice_2018.status == NoticeStatus.TRANSFORMED