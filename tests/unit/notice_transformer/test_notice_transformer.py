import pathlib
import tempfile
from collections import Counter

from ted_sws.domain.model.notice import NoticeStatus
from ted_sws.notice_transformer.services.notice_transformer import NoticeTransformer, transform_notice, \
    transform_test_data


def test_notice_transformer(fake_rml_mapper, fake_mapping_suite, notice_2018):
    notice_transformer = NoticeTransformer(mapping_suite=fake_mapping_suite, rml_mapper=fake_rml_mapper)
    notice_2018._status = NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION
    notice_transformer.transform_notice(notice=notice_2018)
    assert notice_2018.status == NoticeStatus.TRANSFORMED


def test_notice_transformer_function(fake_rml_mapper, fake_mapping_suite, notice_2018):
    notice_2018._status = NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION
    result_notice = transform_notice(notice_2018, fake_mapping_suite, fake_rml_mapper)
    assert result_notice.status == NoticeStatus.TRANSFORMED


def test_transform_test_data(fake_rml_mapper, fake_mapping_suite):
    notice_transformer = NoticeTransformer(mapping_suite=fake_mapping_suite, rml_mapper=fake_rml_mapper)
    with tempfile.TemporaryDirectory() as d:
        output_path = pathlib.Path(d)
        notice_transformer.transform_test_data(output_path=output_path)
        file_names = [file.name for file in output_path.iterdir() if file.is_file()]
        test_data = fake_mapping_suite.transformation_test_data.test_data
        test_data_file_names = [data.file_name for data in test_data]
        assert Counter(file_names) == Counter(test_data_file_names)


def test_transform_test_data_function(fake_rml_mapper, fake_mapping_suite):
    with tempfile.TemporaryDirectory() as d:
        output_path = pathlib.Path(d)
        transform_test_data(mapping_suite=fake_mapping_suite, rml_mapper=fake_rml_mapper, output_path=output_path)
        file_names = [file.name for file in output_path.iterdir() if file.is_file()]
        test_data = fake_mapping_suite.transformation_test_data.test_data
        test_data_file_names = [data.file_name for data in test_data]
        assert Counter(file_names) == Counter(test_data_file_names)
