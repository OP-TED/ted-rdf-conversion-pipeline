import abc
import tempfile
from pathlib import Path

from ted_sws.core.model.manifestation import RDFManifestation, XMLManifestation
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.core.model.transform import MappingSuite, FileResource
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapperABC, SerializationFormat as RMLSerializationFormat

DATA_SOURCE_PACKAGE = "data"


def transform_notice(notice: Notice, mapping_suite: MappingSuite, rml_mapper: RMLMapperABC):
    """
        This function allows the XML content of a Notice to be transformed into RDF,
         using the mapping rules in mapping_suite and the rml_mapper mapping adapter.
    :param notice:
    :param mapping_suite:
    :param rml_mapper:
    :return:
    """
    return NoticeTransformer(mapping_suite=mapping_suite, rml_mapper=rml_mapper).transform_notice(notice=notice)


def transform_test_data(mapping_suite: MappingSuite, rml_mapper: RMLMapperABC, output_path: Path):
    """
        This function converts each file in the test data and writes the result to a file in output_path.
    :param mapping_suite:
    :param rml_mapper:
    :param output_path:
    :return:
    """
    NoticeTransformer(mapping_suite=mapping_suite, rml_mapper=rml_mapper).transform_test_data(
        output_path=output_path,
    )


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

    @staticmethod
    @abc.abstractmethod
    def get_test_notice_container(filename: str) -> str:
        """
            Get filename name (notice container) without extension
        :param filename:
        :return:
        """


class NoticeTransformer(NoticeTransformerABC):
    """
        This class is a concrete implementation of transforming a notice using rml-mapper.
    """

    def __init__(self, mapping_suite: MappingSuite, rml_mapper: RMLMapperABC):
        self.mapping_suite = mapping_suite
        self.rml_mapper = rml_mapper

    def _write_notice_xml_manifestation_in_package(self, package_path: Path, notice: Notice):
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

    @staticmethod
    def get_test_notice_container(filename: str) -> str:
        return NoticeTransformer._get_filename_name(filename)

    @staticmethod
    def _get_filename_name(filename: str) -> str:
        """
        Get filename name without extension
        :param filename:
        :return:
        """
        return Path(filename).stem

    def _get_out_file_ext(self, filename: str) -> str:
        """
        Get file extension, based on output format
        :param filename:
        :param ext:
        :return:
        """
        serialization: RMLSerializationFormat = self.rml_mapper.get_serialization_format()
        exts = {
            RMLSerializationFormat.TURTLE: '.ttl'
        }
        return "{ext}".format(ext=exts.get(serialization, Path(filename).suffix))

    def _write_resource_to_out_file(self, file_resource: FileResource, output_path: Path):
        filename = file_resource.file_name
        notice_container = self.get_test_notice_container(filename)
        out_filename = notice_container + self._get_out_file_ext(filename)
        file_resource_parent_path = output_path / Path(notice_container)
        file_resource_parent_path.mkdir(parents=True, exist_ok=True)
        file_resource_path = file_resource_parent_path / Path(out_filename)
        with file_resource_path.open("w+", encoding="utf-8") as f:
            f.write(file_resource.file_content)

    def transform_test_data(self, output_path: Path):
        """
            This method converts each file in the test data and writes the result to a file in output_path.
        :param output_path:
        :return:
        """
        transformation_test_data = self.mapping_suite.transformation_test_data
        output_path.mkdir(parents=True, exist_ok=True)
        # file_resources = []
        for data in transformation_test_data.test_data:
            notice = Notice(ted_id="tmp_notice", xml_manifestation=XMLManifestation(object_data=data.file_content))
            notice._status = NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION
            notice_result = self.transform_notice(notice=notice)
            file_resource = FileResource(
                file_name=data.file_name,
                file_content=notice_result.rdf_manifestation.object_data
            )
            self._write_resource_to_out_file(file_resource, output_path)
            # file_resources.append(file_resource)

        # for file_resource in file_resources:
        #    self._write_resource_to_out_file(file_resource, output_path)

    def transform_notice(self, notice: Notice) -> Notice:
        """
            This method performs the transformation on a notice.
        :param notice:
        :return:
        """
        with tempfile.TemporaryDirectory() as d:
            package_path = Path(d) / self.mapping_suite.identifier
            self._write_notice_xml_manifestation_in_package(package_path=package_path, notice=notice)
            rdf_result = self.rml_mapper.execute(package_path=package_path)
            notice.set_rdf_manifestation(rdf_manifestation=RDFManifestation(object_data=rdf_result))
        return notice
