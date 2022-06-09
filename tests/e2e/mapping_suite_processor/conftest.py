import pytest

from ted_sws import config
from ted_sws.mapping_suite_processor.adapters.allegro_triple_store import AllegroGraphTripleStore
from tests import TEST_DATA_PATH


@pytest.fixture
def file_system_repository_path():
    return TEST_DATA_PATH / "notice_transformer" / "mapping_suite_processor_repository"

@pytest.fixture
def yarrrml_file_content():
    return """prefixes:
 ex: "http://example.com/"

mappings:
  person:
    sources:
      - ['data.json~jsonpath', '$.persons[*]']
    s: http://example.com/$(firstname)
    po:
      - [a, foaf:Person]
      - [ex:name, $(firstname)]
"""

@pytest.fixture
def rml_file_result():
    return """@prefix rr: <http://www.w3.org/ns/r2rml#>.
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix fnml: <http://semweb.mmlab.be/ns/fnml#>.
@prefix fno: <https://w3id.org/function/ontology#>.
@prefix d2rq: <http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#>.
@prefix void: <http://rdfs.org/ns/void#>.
@prefix dc: <http://purl.org/dc/terms/>.
@prefix foaf: <http://xmlns.com/foaf/0.1/>.
@prefix rml: <http://semweb.mmlab.be/ns/rml#>.
@prefix ql: <http://semweb.mmlab.be/ns/ql#>.
@prefix : <http://mapping.example.com/>.
@prefix ex: <http://example.com/>.

:rules_000 a void:Dataset;
    void:exampleResource :map_person_000.
:map_person_000 rml:logicalSource :source_000.
:source_000 a rml:LogicalSource;
    rml:source "data.json";
    rml:iterator "$.persons[*]";
    rml:referenceFormulation ql:JSONPath.
:map_person_000 a rr:TriplesMap;
    rdfs:label "person".
:s_000 a rr:SubjectMap.
:map_person_000 rr:subjectMap :s_000.
:s_000 rr:template "http://example.com/{firstname}".
:pom_000 a rr:PredicateObjectMap.
:map_person_000 rr:predicateObjectMap :pom_000.
:pm_000 a rr:PredicateMap.
:pom_000 rr:predicateMap :pm_000.
:pm_000 rr:constant rdf:type.
:pom_000 rr:objectMap :om_000.
:om_000 a rr:ObjectMap;
    rr:constant "http://xmlns.com/foaf/0.1/Person";
    rr:termType rr:IRI.
:pom_001 a rr:PredicateObjectMap.
:map_person_000 rr:predicateObjectMap :pom_001.
:pm_001 a rr:PredicateMap.
:pom_001 rr:predicateMap :pm_001.
:pm_001 rr:constant ex:name.
:pom_001 rr:objectMap :om_001.
:om_001 a rr:ObjectMap;
    rml:reference "firstname";
    rr:termType rr:Literal.

"""

@pytest.fixture
def ttl_file():
    path = TEST_DATA_PATH / "notice_transformer" / "test_repository" / "test_package" / "transformation" / "mappings" / "award_of_contract.rml.ttl"
    return path.read_text()


@pytest.fixture
def path_ttl_file():
    path = TEST_DATA_PATH / "notice_transformer" / "test_repository" / "test_package" / "transformation" / "mappings" / "complementary_information.rml.ttl"
    return str(path)


@pytest.fixture
def package_folder_path():
    return TEST_DATA_PATH / "notice_validator" / "test_repository" / "test_package"


@pytest.fixture
def allegro_triple_store():
    return AllegroGraphTripleStore(host=config.ALLEGRO_HOST, user=config.AGRAPH_SUPER_USER,
                                   password=config.AGRAPH_SUPER_PASSWORD)