import pathlib

from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapperABC, SerializationFormat


class FakeRMLMapper(RMLMapperABC):

    def get_serialization_format(self) -> SerializationFormat:
        return SerializationFormat.TURTLE

    def execute(self, package_path: pathlib.Path) -> str:
        return "RDF result"