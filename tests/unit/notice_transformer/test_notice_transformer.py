import pathlib
import tempfile
from collections import Counter

import pytest

from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB
from ted_sws.notice_transformer.services.notice_transformer import transform_notice, \
    transform_test_data, transform_notice_by_id


def test_notice_transformer_function(fake_rml_mapper, fake_mapping_suite, notice_2018):
    notice_2018._status = NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION
    result_notice = transform_notice(notice_2018, fake_mapping_suite, fake_rml_mapper)
    assert result_notice.status == NoticeStatus.TRANSFORMED


def test_notice_transformer_by_id_function(fake_rml_mapper, mongodb_client, fake_mapping_suite, notice_2018,
                                           notice_repository):
    notice_2018._status = NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION
    notice_repository.add(notice=notice_2018)
    notice_id = notice_2018.ted_id
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_suite_repository.add(mapping_suite=fake_mapping_suite)
    mapping_suite_id = fake_mapping_suite.get_mongodb_id()
    transform_notice_by_id(notice_id, mapping_suite_id, notice_repository, mapping_suite_repository,
                           fake_rml_mapper)
    result_notice = notice_repository.get(reference=notice_id)
    assert result_notice.status == NoticeStatus.TRANSFORMED


def test_notice_transformer_by_id_function_with_invalid_ids(fake_rml_mapper, mongodb_client, fake_mapping_suite,
                                                            notice_2018,
                                                            notice_repository, aggregates_database_name):
    notice_2018._status = NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION
    notice_id = notice_2018.ted_id
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    with pytest.raises(Exception):
        transform_notice_by_id(notice_id, fake_mapping_suite.identifier, notice_repository, mapping_suite_repository,
                               fake_rml_mapper)
    result_notice = notice_repository.get(reference=notice_id)
    assert result_notice is None
    notice_repository.add(notice=notice_2018)
    mongodb_client.drop_database(aggregates_database_name)
    with pytest.raises(Exception):
        transform_notice_by_id(notice_id, fake_mapping_suite.identifier, notice_repository, mapping_suite_repository,
                               fake_rml_mapper)
    result_notice = notice_repository.get(reference=notice_id)
    assert result_notice.status == NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION


def test_transform_test_data_function(fake_rml_mapper, fake_mapping_suite):
    with tempfile.TemporaryDirectory() as d:
        output_path = pathlib.Path(d)
        transform_test_data(mapping_suite=fake_mapping_suite, rml_mapper=fake_rml_mapper, output_path=output_path)
        file_names = [path.stem for path in output_path.glob("**/*.ttl")]
        test_data = fake_mapping_suite.transformation_test_data.test_data
        test_data_file_names = [pathlib.Path(data.file_name).stem for data in test_data]
        assert Counter(file_names) == Counter(test_data_file_names)
