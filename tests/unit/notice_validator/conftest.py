from pathlib import Path

import pytest

from ted_sws.core.model.manifestation import RDFManifestation, XMLManifestation, XPATHCoverageValidationReport, \
    XPATHCoverageValidationResult, SHACLTestSuiteValidationReport, SPARQLTestSuiteValidationReport
from ted_sws.core.model.notice import NoticeStatus, Notice
from ted_sws.core.model.transform import FileResource, SPARQLTestSuite, MetadataConstraints, TransformationRuleSet, \
    SHACLTestSuite, TransformationTestData, MappingSuite
from tests import TEST_DATA_PATH


@pytest.fixture
def query_content():
    return """# title: Official name
# description: this is a description
PREFIX epo: <http://data.europa.eu/a4g/ontology#>
ASK
WHERE
{
  ?this epo:playedBy / epo:hasDefaultContactPoint / epo:hasFax ?organisationContactPointFax .
}
    """


@pytest.fixture
def query_content_without_description():
    return """

    # title : Official name

    PREFIX epo: <http://data.europa.eu/a4g/ontology#>
    ASK
    WHERE
    {
      ?this epo:playedBy / epo:hasDefaultContactPoint / epo:hasFax ?organisationContactPointFax .
    }
        """


@pytest.fixture
def query_content_with_xpath():
    return """
    #title: Official name
    #xpath: //some/xpath/goes/here
    #description: this is a description

    PREFIX epo: <http://data.europa.eu/a4g/ontology#>
    ASK
    WHERE
    {
      ?this epo:playedBy / epo:hasDefaultContactPoint / epo:hasFax ?organisationContactPointFax .
    }
        """


@pytest.fixture
def rdf_file_content():
    path = TEST_DATA_PATH / "example.ttl"
    return path.read_text()


@pytest.fixture
def shacl_file_content():
    path = TEST_DATA_PATH / "ePO_shacl_shapes.xml"
    return path.read_text()


@pytest.fixture
def shacl_file_two_content():
    path = TEST_DATA_PATH / "ePO_shacl_shapes_two.xml"
    return path.read_text()


@pytest.fixture
def list_of_shacl_files(shacl_file_content, shacl_file_two_content):
    return [
        FileResource(file_name="shacl_file_one.xml", file_content=shacl_file_content),
        FileResource(file_name="shacl_file_two.xml", file_content=shacl_file_two_content)
    ]


@pytest.fixture
def shacl_file_one(shacl_file_content):
    return FileResource(file_name="shacl_file_one.xml", file_content=shacl_file_content)


@pytest.fixture
def shacl_file_two(shacl_file_two_content):
    return FileResource(file_name="shacl_file_two.xml", file_content=shacl_file_two_content)


@pytest.fixture
def shacl_file_with_error():
    return FileResource(file_name="shacl_file_with_error", file_content="something fishy")


@pytest.fixture
def validator_query():
    return """
prefix dash: <http://datashapes.org/dash#>
prefix sh: <http://www.w3.org/ns/shacl#>
prefix message: <http://www.w3.org/ns/shacl#message>

SELECT ?focusNode ?message ?resultPath ?resultSeverity ?sourceConstraintComponent ?sourceShape ?value
WHERE {
    ?vr a sh:ValidationResult .
    ?vr sh:focusNode ?focusNode .
    OPTIONAL {
        ?vr sh:message ?message .
    }
    OPTIONAL {
        ?vr sh:resultPath ?resultPath .
    }
    OPTIONAL {
        ?vr sh:resultSeverity ?resultSeverity .
    }
    OPTIONAL {
        ?vr sh:sourceConstraintComponent ?sourceConstraintComponent .
    }
    OPTIONAL {
        ?vr sh:sourceShape ?sourceShape .
    }
    OPTIONAL {
        ?vr sh:value ?value .
    }
}
ORDER BY ?focusNode ?resultSeverity ?sourceConstraintComponent
    """


@pytest.fixture
def sparql_file_one():
    query = """#title: Title One
#description: this is a description
#xpath: /TED_EXPORT/FORM_SECTION/F03_2014/OBJECT_CONTRACT/VAL_TOTAL/@CURRENCY

PREFIX epo: <http://data.europa.eu/a4g/ontology#>
ASK
WHERE
{
  ?this epo:playedBy / epo:hasDefaultContactPoint / epo:hasFax ?organisationContactPointFax .
}
    """
    return FileResource(file_name="good_file", file_content=query)


@pytest.fixture
def sparql_file_two():
    query = """#title: Title Two
#description: this is a description
#xpath: /TED_EXPORT/FORM_SECTION/F03_2014/LEGAL_BASIS/@VALUE

PREFIX epo: <http://data.europa.eu/a4g/ontology#>
ASK
WHERE
{
  ?this epo:IsRoleOf / epo:hasName ?value .
}
    """
    return FileResource(file_name="better_file", file_content=query)


@pytest.fixture
def sparql_file_select():
    query = """#title: Title One
#description: this is a description
#xpath: /TED_EXPORT/FORM_SECTION/F03_2014/OBJECT_CONTRACT/VAL_TOTAL/@CURRENCY

PREFIX epo: <http://data.europa.eu/a4g/ontology#>
SELECT ?name
WHERE
{
  ?this epo:playedBy / epo:hasDefaultContactPoint / epo:hasFax ?organisationContactPointFax .
}
    """
    return FileResource(file_name="select_file", file_content=query)


@pytest.fixture
def invalid_sparql_file():
    query = """#title: Title Two
#description: this is a description
#xpath: /some/xpath

ASK
WHERE
{
  ?this hasName ?value .
}
    """
    return FileResource(file_name="some_file", file_content=query)


@pytest.fixture
def false_query_sparql_file():
    query = """#title: Title Two
#description: this is a description
#xpath: /some/xpath

PREFIX epo: <http://data.europa.eu/a4g/ontology#>
ASK
WHERE
{
  ?this epo:hasNameFalse ?value .
}
    """
    return FileResource(file_name="some_file", file_content=query)


@pytest.fixture
def sparql_test_suite(sparql_file_one, sparql_file_two):
    return SPARQLTestSuite(identifier="sparql_test_package", sparql_tests=[sparql_file_one, sparql_file_two])


@pytest.fixture
def shacl_test_suite(shacl_file_one, shacl_file_two):
    return SHACLTestSuite(identifier="shacl_test_package", shacl_tests=[shacl_file_one, shacl_file_two])


@pytest.fixture
def bad_shacl_test_suite(shacl_file_one, shacl_file_with_error):
    return SHACLTestSuite(identifier="bad_shacl_test_package", shacl_tests=[shacl_file_one, shacl_file_with_error])


@pytest.fixture
def sparql_test_suite_with_invalid_query(invalid_sparql_file):
    return SPARQLTestSuite(identifier="sparql_test_package", sparql_tests=[invalid_sparql_file])


@pytest.fixture
def sparql_test_suite_with_false_query(false_query_sparql_file):
    return SPARQLTestSuite(identifier="sparql_test_package", sparql_tests=[false_query_sparql_file])


@pytest.fixture
def sparql_test_suite_with_select_query(sparql_file_select):
    return SPARQLTestSuite(identifier="sparql_test_package", sparql_tests=[sparql_file_select])


@pytest.fixture
def dummy_mapping_suite(sparql_test_suite, shacl_test_suite):
    metadata_constrains = MetadataConstraints(constraints=dict())
    file_name = "fake_title.txt"
    empty_file_resource = FileResource(file_name=file_name, file_content="no content here", original_name=file_name)
    transformation_rule_set = TransformationRuleSet(resources=[empty_file_resource],
                                                    rml_mapping_rules=[empty_file_resource]
                                                    )
    shacl_test_suite = shacl_test_suite
    sparql_test_suite = sparql_test_suite
    transformation_test_data = TransformationTestData(test_data=[empty_file_resource])
    mapping_suite = MappingSuite(metadata_constraints=metadata_constrains,
                                 transformation_rule_set=transformation_rule_set,
                                 shacl_test_suites=[shacl_test_suite],
                                 sparql_test_suites=[sparql_test_suite],
                                 transformation_test_data=transformation_test_data
                                 )
    return mapping_suite


@pytest.fixture
def path_to_file_system_repository():
    return TEST_DATA_PATH / "notice_transformer" / "test_repository"


@pytest.fixture
def notice_with_distilled_status(notice_2020, rdf_file_content):
    notice_2020.update_status_to(new_status=NoticeStatus.INDEXED)
    notice_2020.update_status_to(new_status=NoticeStatus.NORMALISED_METADATA)
    notice_2020.update_status_to(new_status=NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION)
    notice_2020.update_status_to(new_status=NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION)
    notice_2020.set_rdf_manifestation(rdf_manifestation=RDFManifestation(object_data=rdf_file_content))
    notice_2020.set_distilled_rdf_manifestation(
        distilled_rdf_manifestation=RDFManifestation(object_data=rdf_file_content))
    notice_2020.update_status_to(new_status=NoticeStatus.DISTILLED)

    return notice_2020


@pytest.fixture
def fake_repository_path():
    return TEST_DATA_PATH / "notice_validator" / "test_repository"


@pytest.fixture
def fake_validation_repository_path():
    return TEST_DATA_PATH / "notice_validator" / "validation_repository"


@pytest.fixture
def fake_validation_mapping_suite_id() -> str:
    return "validation_package"


@pytest.fixture
def fake_validation_notice_id() -> str:
    return "292288-2021"


@pytest.fixture
def fake_mapping_suite_id() -> str:
    return "test_package"


@pytest.fixture
def fake_sparql_mapping_suite_id() -> str:
    return "test_sparql_package"


@pytest.fixture
def fake_mapping_suite_F03_id() -> str:
    return "test_package_F03"


@pytest.fixture
def invalid_mapping_suite_id() -> str:
    return "test_invalid_package"


@pytest.fixture
def fake_notice_id() -> str:
    return "notice"


@pytest.fixture
def fake_mapping_suite_F03_path(fake_repository_path, fake_mapping_suite_F03_id) -> Path:
    return fake_repository_path / fake_mapping_suite_F03_id


@pytest.fixture
def fake_conceptual_mappings_F03_path(fake_repository_path, fake_mapping_suite_F03_id) -> str:
    return str(fake_repository_path / fake_mapping_suite_F03_id / "transformation" / "conceptual_mappings.xlsx")


@pytest.fixture
def fake_notice_F03_content(fake_repository_path, fake_mapping_suite_F03_id):
    with open(fake_repository_path / fake_mapping_suite_F03_id / "test_data" / "1" / "notice.xml") as f:
        notice_content = f.read()
    return notice_content


@pytest.fixture
def fake_notice_F03(fake_notice_F03_content, fake_notice_id):
    xml_manifestation = XMLManifestation(object_data=fake_notice_F03_content)
    notice = Notice(ted_id=fake_notice_id, xml_manifestation=xml_manifestation)
    rdf_manifestation = RDFManifestation(object_data="RDF manifestation content",
                                         shacl_validations=[],
                                         sparql_validations=[]
                                         )
    notice._rdf_manifestation = rdf_manifestation
    notice._distilled_rdf_manifestation = rdf_manifestation
    return notice


@pytest.fixture
def fake_xml_manifestation_with_coverage_for_sparql_runner() -> XMLManifestation:
    xml_manifestation = XMLManifestation(object_data="")
    xpath_coverage_validation = {
        "mapping_suite_identifier": 'package_F03',
        "xpath_covered": [
            '/TED_EXPORT/FORM_SECTION/F03_2014/LEGAL_BASIS/@VALUE',
            '/TED_EXPORT/FORM_SECTION/F03_2014/OBJECT_CONTRACT/VAL_TOTAL/@CURRENCY'
        ],
        "xpath_not_covered": [
            '/TED_EXPORT/FORM_SECTION/F03_2014/CONTRACTING_BODY/ADDRESS_CONTRACTING_BODY/COUNTRY/@VALUE',
            '/TED_EXPORT/FORM_SECTION/F03_2014/CONTRACTING_BODY/CA_ACTIVITY/@VALUE',
            '/TED_EXPORT/FORM_SECTION/F03_2014/AWARD_CONTRACT/AWARDED_CONTRACT/CONTRACTORS'
        ]
    }
    xml_manifestation.xpath_coverage_validation = XPATHCoverageValidationReport(
        object_data="",
        mapping_suite_identifier="package_F03"
    )
    xml_manifestation.xpath_coverage_validation.validation_result = XPATHCoverageValidationResult(
        **xpath_coverage_validation)

    return xml_manifestation

@pytest.fixture
def fake_validation_notice():
    xml_manifestation = XMLManifestation(object_data="")
    xpath_coverage_validation = {
        "mapping_suite_identifier": 'package_F03',
        "xpath_covered": [
            '/TED_EXPORT/FORM_SECTION/F03_2014/LEGAL_BASIS/@VALUE',
            '/TED_EXPORT/FORM_SECTION/F03_2014/OBJECT_CONTRACT/VAL_TOTAL/@CURRENCY'
        ],
        "xpath_not_covered": [
            '/TED_EXPORT/FORM_SECTION/F03_2014/CONTRACTING_BODY/ADDRESS_CONTRACTING_BODY/COUNTRY/@VALUE',
            '/TED_EXPORT/FORM_SECTION/F03_2014/CONTRACTING_BODY/CA_ACTIVITY/@VALUE',
            '/TED_EXPORT/FORM_SECTION/F03_2014/AWARD_CONTRACT/AWARDED_CONTRACT/CONTRACTORS'
        ]
    }
    xml_manifestation.xpath_coverage_validation = XPATHCoverageValidationReport(
        object_data="",
        mapping_suite_identifier="package_F03"
    )
    xml_manifestation.xpath_coverage_validation.validation_result = XPATHCoverageValidationResult(
        **xpath_coverage_validation)
    notice = Notice(ted_id="validation_notice_id", xml_manifestation=xml_manifestation)
    sparql_validations = [SPARQLTestSuiteValidationReport(**{
        "object_data": '62f037e2a5458a3a6776138c',
        "created": '2022-08-07T20:49:15.500870',
        "mapping_suite_identifier": 'package_F03',
        "test_suite_identifier": 'cm_assertions',
        "validation_results": [
            {
                "query": {
                    "title": 'II.1.7.4 - Currency',
                    "description": '“II.1.7.4 - Currency” in SF corresponds to “nan nan” in eForms. The corresponding XML element is /TED_EXPORT/FORM_SECTION/F03_2014/OBJECT_CONTRACT/VAL_TOTAL/@CURRENCY. The expected ontology instances are epo: epo:ResultNotice / epo:NoticeAwardInformation / epo:MonetaryValue / at-voc:currency (from currency.json) .',
                    "query": 'PREFIX epo: <http://data.europa.eu/a4g/ontology#>\n\nASK WHERE { { ?this epo:announcesNoticeAwardInformation / epo:hasTotalAwardedValue / epo:hasCurrency ?value } UNION { ?this epo:announcesNoticeAwardInformation / epo:hasProcurementLowestReceivedTenderValue / epo:hasCurrency ?value } UNION  { ?this epo:announcesNoticeAwardInformation / epo:hasProcurementHighestReceivedTenderValue / epo:hasCurrency ?value }  }'
                },
                "result": 'True',
                "error": None,
                "identifier": 'sparql_query_46'
            },
            {
                "query": {
                    "title": "",
                    "description": "",
                    "query": ""
                },
                "result": 'False',
                "error": "SOME_ERROR",
                "identifier": 'sparql_query_46'
            }
        ]
    })]
    shacl_validations = [SHACLTestSuiteValidationReport(**{
        "object_data": '62f037e2a5458a3a6776138a',
        "created": '2022-08-07T20:49:15.500870',
        "mapping_suite_identifier": 'package_F03',
        "test_suite_identifier": 'epo',
        "validation_results": {
            "conforms": 'False',
            "results_dict": {
                "results": {
                    "bindings": [
                        {
                            "focusNode": {
                                "type": 'uri',
                                "value": 'http://data.europa.eu/a4g/resource/ContactPoint/2021-S-250-663165/ab152979-15bf-30c3-b6f3-e0c554cfa9d0'
                            },
                            "message": {
                                "type": 'literal',
                                "value": 'Value is not Literal with datatype xsd:anyURI'
                            },
                            "resultPath": {
                                "type": 'uri',
                                "value": 'http://data.europa.eu/a4g/ontology#hasInternetAddress'
                            },
                            "resultSeverity": {
                                "type": 'uri',
                                "value": 'http://www.w3.org/ns/shacl#Violation'
                            },
                            "sourceConstraintComponent": {
                                "type": 'uri',
                                "value": 'http://www.w3.org/ns/shacl#DatatypeConstraintComponent'
                            },
                            "sourceShape": {
                                "type": 'bnode',
                                "value": 'Nb24b2cf50dcc4b8cbe40e95f3d032394'
                            },
                            "value": {
                                "type": 'literal',
                                "value": 'http://www.lshp.fi'
                            }
                        },
                        {
                            "resultSeverity": {
                                "type": 'uri',
                                "value": 'http://www.w3.org/ns/shacl#Info'
                            }
                        },
                        {
                            "resultSeverity": {
                                "type": 'uri',
                                "value": 'http://www.w3.org/ns/shacl#Warning'
                            }
                        }
                    ]
                }
            }
        }
    })]

    rdf_manifestation = RDFManifestation(object_data="RDF manifestation content",
                                         shacl_validations=shacl_validations,
                                         sparql_validations=sparql_validations
                                         )
    notice._rdf_manifestation = rdf_manifestation
    notice._distilled_rdf_manifestation = rdf_manifestation
    return notice
