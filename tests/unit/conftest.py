from tests.fakes.fake_rml_mapper import FakeRMLMapper
import pytest
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapperABC, SerializationFormat as RMLSerializationFormat


@pytest.fixture
def fake_rml_mapper() -> RMLMapperABC:
    rml_mapper = FakeRMLMapper()
    rml_mapper.set_serialization_format(RMLSerializationFormat.TURTLE)
    return rml_mapper
