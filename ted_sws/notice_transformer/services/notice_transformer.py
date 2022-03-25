import abc
import pathlib
import tempfile

from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem, \
    TRANSFORM_PACKAGE_NAME, RESOURCES_PACKAGE_NAME
from ted_sws.domain.model.manifestation import RDFManifestation, XMLManifestation
from ted_sws.domain.model.notice import Notice, NoticeStatus
from ted_sws.domain.model.transform import MappingSuite, FileResource
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapperABC

DATA_SOURCE_PACKAGE = "data"


def transform_notice(notice: Notice, mapping_suite: MappingSuite, rml_mapper: RMLMapperABC):
    """
        This feature allows the XML content of a Notice to be transformed into RDF,
         using the mapping rules in mapping_suite and the rml_mapper mapping adapter.
    :param notice:
    :param mapping_suite:
    :param rml_mapper:
    :return:
    """
    return NoticeTransformer(mapping_suite=mapping_suite, rml_mapper=rml_mapper).transform_notice(notice=notice)


def transform_test_data(mapping_suite: MappingSuite, rml_mapper: RMLMapperABC, output_path: pathlib.Path):
    """

    :param mapping_suite:
    :param rml_mapper:
    :param output_path:
    :return:
    """
    NoticeTransformer(mapping_suite=mapping_suite, rml_mapper=rml_mapper).transform_test_data(output_path=output_path)


class NoticeTransformerABC(abc.ABC):
    """
        This class is a general interface for transforming a notice.
    """

    @abc.abstractmethod
    def transform_notice(self, notice: Notice) -> Notice:
        """
            This method performs the transformation on a notice.
        :param notice:
        :return:
        """


class NoticeTransformer(NoticeTransformerABC):
    """
        This class is a concrete implementation of transforming a notice using rml-mapper.
    """

    def __init__(self, mapping_suite: MappingSuite, rml_mapper: RMLMapperABC):
        self.mapping_suite = mapping_suite
        self.rml_mapper = rml_mapper

    def _write_notice_xml_manifestation_in_package(self, package_path: pathlib.Path, notice: Notice):
        """
            This method generates a source file to perform the transformation.
        :param package_path:
        :param notice:
        :return:
        """
        mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=package_path.parent)
        mapping_suite_repository.add(mapping_suite=self.mapping_suite)
        data_source_path = package_path / DATA_SOURCE_PACKAGE
        data_source_path.mkdir(parents=True, exist_ok=True)
        notice_path = data_source_path / "source.xml"
        with notice_path.open("w", encoding="utf-8") as file:
            file.write(notice.xml_manifestation.object_data)

    def transform_test_data(self, output_path: pathlib.Path):
        """
            This method converts each file in the test data and writes the result to a file in output_path.
        :param output_path:
        :return:
        """
        transformation_test_data = self.mapping_suite.transformation_test_data
        file_resources = []
        for data in transformation_test_data.test_data:
            notice = Notice(ted_id="tmp_notice",xml_manifestation=XMLManifestation(object_data=data.file_content))
            notice._status = NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION
            notice_result = self.transform_notice(notice=notice)
            file_resources.append(
                FileResource(file_name=data.file_name, file_content=notice_result.rdf_manifestation.object_data))

        output_path.mkdir(parents=True, exist_ok=True)
        for file_resource in file_resources:
            file_resource_path = output_path / file_resource.file_name
            with file_resource_path.open("w", encoding="utf-8") as f:
                f.write(file_resource.file_content)

    def transform_notice(self, notice: Notice) -> Notice:
        """
            This method performs the transformation on a notice.
        :param notice:
        :return:
        """
        with tempfile.TemporaryDirectory() as d:
            package_path = pathlib.Path(d) / self.mapping_suite.identifier
            self._write_notice_xml_manifestation_in_package(package_path=package_path, notice=notice)
            rdf_result = self.rml_mapper.execute(package_path=package_path)
            notice.set_rdf_manifestation(rdf_manifestation=RDFManifestation(object_data=rdf_result))
        return notice
