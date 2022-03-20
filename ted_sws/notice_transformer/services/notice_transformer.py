import abc

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




    def transform_notice(self, notice: Notice):
        """
            This method performs the transformation on a notice.
        :param notice:
        :return:
        """
        
