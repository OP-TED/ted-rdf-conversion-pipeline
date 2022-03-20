import abc
import pathlib
import tempfile

from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.domain.model.manifestation import RDFManifestation
from ted_sws.domain.model.notice import Notice
from ted_sws.domain.model.transform import MappingSuite
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapperABC


class NoticeTransformerABC(abc.ABC):
    """
        This class is a general interface for transforming a notice.
    """
    @abc.abstractmethod
    def transform_notice(self, notice: Notice):
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


    def _inject_in_package_notice_xml_manifestation(self, package_path: pathlib.Path, notice: Notice):
        mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=package_path.parent)
        mapping_suite_repository.add(mapping_suite=self.mapping_suite)
        notice_path = package_path / "transform" / "resources" / "notice.xml"
        with notice_path.open("w", encoding="utf-8") as file:
            file.write(notice.xml_manifestation.object_data)

    def transform_notice(self, notice: Notice):
        """
            This method performs the transformation on a notice.
        :param notice:
        :return:
        """
        with tempfile.TemporaryDirectory() as d:
            package_path = pathlib.Path(d) / self.mapping_suite.identifier
            self._inject_in_package_notice_xml_manifestation(package_path=package_path, notice=notice)
            rdf_result = self.rml_mapper.execute(package_path=package_path)
            notice.set_rdf_manifestation(rdf_manifestation=RDFManifestation(object_data=rdf_result))




