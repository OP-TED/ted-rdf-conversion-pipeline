import base64
import json

import pytest

from ted_sws.core.model.manifestation import SPARQLTestSuiteValidationReport, SHACLTestSuiteValidationReport, \
    RDFManifestation, METSManifestation, XMLManifestation
from ted_sws.core.model.metadata import NormalisedMetadata, LanguageTaggedString, TEDMetadata
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepositoryInFileSystem
from ted_sws.metadata_normaliser.services.metadata_normalizer import LANGUAGE_KEY, XSD_VERSION_KEY, E_FORMS_SUBTYPE_KEY, \
    EXTRACTED_LEGAL_BASIS_KEY, PLACE_OF_PERFORMANCE_KEY, FORM_TYPE_KEY, NOTICE_TYPE_KEY, DEADLINE_DATE_KEY, \
    SENT_DATE_KEY
#
# ARBITRARY_RDF_TURTLE_STRING = """
# @prefix rr: <http://www.w3.org/ns/r2rml#>.
# @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
# @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
# @prefix fnml: <http://semweb.mmlab.be/ns/fnml#>.
# @prefix fno: <https://w3id.org/function/ontology#>.
# @prefix d2rq: <http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#>.
# @prefix void: <http://rdfs.org/ns/void#>.
# @prefix dc: <http://purl.org/dc/terms/>.
# @prefix foaf: <http://xmlns.com/foaf/0.1/>.
# @prefix rml: <http://semweb.mmlab.be/ns/rml#>.
# @prefix ql: <http://semweb.mmlab.be/ns/ql#>.
# @prefix : <http://mapping.example.com/>.
# @prefix ex: <http://example.com/>.
#
# :rules_000 a void:Dataset;
#     void:exampleResource :map_person_000.
# :map_person_000 rml:logicalSource :source_000.
# :source_000 a rml:LogicalSource;
#     rml:source "data.json";
#     rml:iterator "$.persons[*]";
#     rml:referenceFormulation ql:JSONPath.
# :map_person_000 a rr:TriplesMap;
#     rdfs:label "person".
# :s_000 a rr:SubjectMap.
# :map_person_000 rr:subjectMap :s_000.
# :s_000 rr:template "http://example.com/{firstname}".
# :pom_000 a rr:PredicateObjectMap.
# :map_person_000 rr:predicateObjectMap :pom_000.
# :pm_000 a rr:PredicateMap.
# :pom_000 rr:predicateMap :pm_000.
# :pm_000 rr:constant rdf:type.
# :pom_000 rr:objectMap :om_000.
# :om_000 a rr:ObjectMap;
#     rr:constant "http://xmlns.com/foaf/0.1/Person";
#     rr:termType rr:IRI.
# :pom_001 a rr:PredicateObjectMap.
# :map_person_000 rr:predicateObjectMap :pom_001.
# :pm_001 a rr:PredicateMap.
# :pom_001 rr:predicateMap :pm_001.
# :pm_001 rr:constant ex:name.
# :pom_001 rr:objectMap :om_001.
# :om_001 a rr:ObjectMap;
#     rml:reference "firstname";
#     rr:termType rr:Literal.
#
# """
# @pytest.fixture
# def normalised_metadata_dict():
#     data = {
#         TITLE_KEY: [
#             LanguageTaggedString(text='Услуги по ремонт и поддържане на превозни средства с военна употреба',
#                                  language='BG'),
#             LanguageTaggedString(text='Repair and maintenance services of military vehicles', language='GA')
#         ],
#         LONG_TITLE_KEY: [
#             LanguageTaggedString(
#                 text='Гepмaния :: Бон :: Услуги по ремонт и поддържане на превозни средства с военна употреба',
#                 language='BG'),
#             LanguageTaggedString(text='Tyskland :: Bonn :: Reparation och underhåll av militärfordon',
#                                  language='SV')
#         ],
#         NOTICE_NUMBER_KEY: '067623-2022',
#         PUBLICATION_DATE_KEY: datetime.date(2022, 2, 7).isoformat(),
#         OJS_NUMBER_KEY: '26',
#         OJS_TYPE_KEY: 'S',
#         BUYER_CITY_KEY: [
#             LanguageTaggedString(text='Бон', language='BG'),
#             LanguageTaggedString(text='Bonn', language='SV')
#         ],
#         BUYER_NAME_KEY: [
#             LanguageTaggedString(text='HIL Heeresinstandsetzungslogistik GmbH', language='DE')
#         ],
#         LANGUAGE_KEY: 'http://publications.europa.eu/resource/authority/language/DEU',
#         BUYER_COUNTRY_KEY: 'http://publications.europa.eu/resource/authority/country/DEU',
#         EU_INSTITUTION_KEY: False,
#         SENT_DATE_KEY: datetime.date(2022, 2, 2).isoformat(),
#         DEADLINE_DATE_KEY: None,
#         NOTICE_TYPE_KEY: 'AWESOME_NOTICE_TYPE',
#         FORM_TYPE_KEY: '18',
#         PLACE_OF_PERFORMANCE_KEY: ['http://data.europa.eu/nuts/code/DE'],
#         EXTRACTED_LEGAL_BASIS_KEY: 'http://publications.europa.eu/resource/authority/legal-basis/32009L0081',
#         FORM_NUMBER_KEY: 'F18',
#         LEGAL_BASIS_DIRECTIVE_KEY: 'http://publications.europa.eu/resource/authority/legal-basis/32009L0081',
#         E_FORMS_SUBTYPE_KEY: 16,
#         XSD_VERSION_KEY: "R2.0.9.S04.E01"
#     }
#
#     return data
#
# @pytest.fixture(scope="function")
# def publicly_available_notice(fetched_notice_data, normalised_metadata_dict) -> Notice:
#     ted_id, original_metadata, xml_manifestation = fetched_notice_data
#     sparql_validation = SPARQLTestSuiteValidationReport(object_data="This is validation report!",
#                                                         test_suite_identifier="sparql_test_id",
#                                                         mapping_suite_identifier="mapping_suite_id",
#                                                         validation_results=[])
#     shacl_validation = SHACLTestSuiteValidationReport(object_data="This is validation report!",
#                                                       test_suite_identifier="shacl_test_id",
#                                                       mapping_suite_identifier="mapping_suite_id",
#                                                       validation_results=[])
#     notice = Notice(ted_id=ted_id, original_metadata=original_metadata,
#                     xml_manifestation=xml_manifestation)
#     notice._rdf_manifestation = RDFManifestation(object_data=ARBITRARY_RDF_TURTLE_STRING,
#                                                  shacl_validations=[shacl_validation],
#                                                  sparql_validations=[sparql_validation]
#                                                  )
#     notice._distilled_rdf_manifestation = RDFManifestation(object_data=ARBITRARY_RDF_TURTLE_STRING,
#                                                            shacl_validations=[shacl_validation],
#                                                            sparql_validations=[sparql_validation]
#                                                            )
#     notice._mets_manifestation = METSManifestation(object_data="METS manifestation content")
#     notice._normalised_metadata = NormalisedMetadata(**normalised_metadata_dict)
#     notice._preprocessed_xml_manifestation = xml_manifestation
#     notice._status = NoticeStatus.PUBLICLY_AVAILABLE
#     return notice
from tests import TEST_DATA_PATH
from tests.conftest import read_notice

NOTICE_REPOSITORY_PATH = TEST_DATA_PATH / "notices"


@pytest.fixture
def transformed_complete_notice():
    test_notice_repository = NoticeRepositoryInFileSystem(repository_path=NOTICE_REPOSITORY_PATH)
    return test_notice_repository.get("396207_2018")
