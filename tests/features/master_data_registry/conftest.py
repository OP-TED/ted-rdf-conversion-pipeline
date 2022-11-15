import pathlib
import pytest
import rdflib

from ted_sws import config
from ted_sws.core.model.manifestation import XMLManifestation, RDFManifestation
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepositoryInFileSystem, NoticeRepository
from ted_sws.data_manager.adapters.sparql_endpoint import SPARQLStringEndpoint
from ted_sws.master_data_registry.services.rdf_fragment_processor import get_subjects_by_cet_uri
from tests import TEST_DATA_PATH

CHILD_NOTICE_ID = "003544-2021"
PARENT_NOTICE_ID = "445564-2020"


@pytest.fixture
def triple_store_endpoint_url() -> str:
    return config.TRIPLE_STORE_ENDPOINT_URL


@pytest.fixture
def mdr_repository_name():
    return "tmp_mdr_test_repository"


@pytest.fixture
def sparql_query_unique_names():
    return """SELECT distinct ?name
            WHERE { ?s a <http://www.w3.org/ns/org#Organization> .
            ?s <http://www.meaningfy.ws/mdr#isCanonicalEntity> True .
            ?s <http://data.europa.eu/a4g/ontology#hasLegalName> ?name .
            }"""


@pytest.fixture
def sparql_query_unique_cet_roots():
    return """SELECT distinct ?s
            WHERE { ?s a <http://www.w3.org/ns/org#Organization> .
            ?s <http://www.meaningfy.ws/mdr#isCanonicalEntity> True .
            }
            """


@pytest.fixture
def rdf_file_path() -> pathlib.Path:
    return TEST_DATA_PATH / "rdf_manifestations" / "002705-2021.ttl"


@pytest.fixture
def rdf_content(rdf_file_path) -> str:
    return rdf_file_path.read_text(encoding="utf-8")


@pytest.fixture
def organisation_cet_uri() -> str:
    return "http://www.w3.org/ns/org#Organization"


@pytest.fixture
def procedure_cet_uri() -> str:
    return "http://data.europa.eu/a4g/ontology#Procedure"


@pytest.fixture
def child_notice() -> Notice:
    notice_repository_path = TEST_DATA_PATH / "notices" / "transformed"
    return NoticeRepositoryInFileSystem(repository_path=notice_repository_path).get(reference="003544-2021")


@pytest.fixture
def notice_procedure_uri(child_notice, procedure_cet_uri) -> rdflib.URIRef:
    rdf_content = child_notice.rdf_manifestation.object_data
    sparql_endpoint = SPARQLStringEndpoint(rdf_content=rdf_content)
    result_uris = get_subjects_by_cet_uri(sparql_endpoint=sparql_endpoint, cet_uri=procedure_cet_uri)
    assert len(result_uris) == 1
    return rdflib.URIRef(result_uris[0])


@pytest.fixture
def parent_notice(child_notice) -> Notice:
    notice_repository_path = TEST_DATA_PATH / "notices" / "transformed"
    return NoticeRepositoryInFileSystem(repository_path=notice_repository_path).get(reference="003544-2021")


@pytest.fixture
def fake_mongodb_client_with_parent_notice(parent_notice, mongodb_client):
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    parent_notice.__dict__["ted_id"] = PARENT_NOTICE_ID
    parent_notice.original_metadata.RN = None
    notice_repository.add(notice=parent_notice)
    return mongodb_client


@pytest.fixture
def notice_with_rdf_manifestation():
    notice = Notice(ted_id="002705-2021", original_metadata={},
                    xml_manifestation=XMLManifestation(object_data="No XML data"))
    rdf_content_path = TEST_DATA_PATH / "rdf_manifestations" / "002705-2021.ttl"
    notice._rdf_manifestation = RDFManifestation(object_data=rdf_content_path.read_text(encoding="utf-8"))
    notice._status = NoticeStatus.TRANSFORMED
    return notice
