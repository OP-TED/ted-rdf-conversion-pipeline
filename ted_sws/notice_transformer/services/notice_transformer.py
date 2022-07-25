import abc
import tempfile
from pathlib import Path

from ted_sws.core.model.manifestation import RDFManifestation, XMLManifestation
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.core.model.transform import MappingSuite, FileResource
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC, MappingSuiteRepositoryABC
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.model.event_message import NoticeEventMessage
from ted_sws.event_manager.services.logger_from_context import get_env_logger
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapperABC, SerializationFormat as RMLSerializationFormat

DATA_SOURCE_PACKAGE = "data"


def transform_notice(notice: Notice, mapping_suite: MappingSuite, rml_mapper: RMLMapperABC) -> Notice:
    """
        This function allows the XML content of a Notice to be transformed into RDF,
         using the mapping rules in mapping_suite and the rml_mapper mapping adapter.
    :param notice:
    :param mapping_suite:
    :param rml_mapper:
    :return:
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        package_path = Path(temp_dir) / mapping_suite.identifier
        mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=package_path.parent)
        mapping_suite_repository.add(mapping_suite=mapping_suite)
        data_source_path = package_path / DATA_SOURCE_PACKAGE
        data_source_path.mkdir(parents=True, exist_ok=True)
        notice_path = data_source_path / "source.xml"
        with notice_path.open("w", encoding="utf-8") as file:
            file.write(notice.xml_manifestation.object_data)
        rdf_result = rml_mapper.execute(package_path=package_path)
        notice.set_rdf_manifestation(rdf_manifestation=RDFManifestation(object_data=rdf_result))
    return notice


def transform_notice_by_id(notice_id: str, mapping_suite_id: str, notice_repository: NoticeRepositoryABC,
                           mapping_suite_repository: MappingSuiteRepositoryABC, rml_mapper: RMLMapperABC):
    """
        This function allows the XML content of a Notice to be transformed into RDF,
         using the mapping rules in mapping_suite and the rml_mapper mapping adapter.
    :param notice_id:
    :param mapping_suite_id:
    :param notice_repository:
    :param mapping_suite_repository:
    :param rml_mapper:
    :return:
    """
    notice = notice_repository.get(reference=notice_id)
    mapping_suite = mapping_suite_repository.get(reference=mapping_suite_id)
    if notice is None:
        raise ValueError(f'Notice, with {notice_id} id, was not found')

    if mapping_suite is None:
        raise ValueError(f'Mapping suite, with {mapping_suite_id} id, was not found')

    result_notice = transform_notice(notice=notice, mapping_suite=mapping_suite, rml_mapper=rml_mapper)
    notice_repository.update(notice=result_notice)


def transform_test_data(mapping_suite: MappingSuite, rml_mapper: RMLMapperABC, output_path: Path,
                        logger: EventLogger = None):
    """
        This function converts each file in the test data and writes the result to a file in output_path.
    :param mapping_suite:
    :param rml_mapper:
    :param output_path:
    :param logger:
    :return:
    """
    logger = get_env_logger(logger)
    transformation_test_data = mapping_suite.transformation_test_data
    output_path.mkdir(parents=True, exist_ok=True)
    test_data = transformation_test_data.test_data

    for idx, data in enumerate(test_data, start=1):
        if logger:
            event_message: NoticeEventMessage = NoticeEventMessage()
            event_message.start_record()

        notice = Notice(ted_id="tmp_notice", xml_manifestation=XMLManifestation(object_data=data.file_content))
        notice._status = NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION
        notice_result = transform_notice(notice, mapping_suite, rml_mapper)
        file_resource = FileResource(
            file_name=data.file_name,
            file_content=notice_result.rdf_manifestation.object_data,
            original_name=data.original_name
        )
        filename = file_resource.file_name
        original_name = file_resource.original_name if file_resource.original_name else filename
        notice_container = Path(filename).stem
        out_filename = Path(original_name).stem + ".ttl"
        file_resource_parent_path = output_path / Path(notice_container)
        file_resource_parent_path.mkdir(parents=True, exist_ok=True)
        file_resource_path = file_resource_parent_path / Path(out_filename)
        with file_resource_path.open("w+", encoding="utf-8") as f:
            f.write(file_resource.file_content)

        if logger:
            notice_id = notice_container
            event_message.message = notice_id
            event_message.notice_id = notice_id
            event_message.end_record()
            logger.info(event_message)
