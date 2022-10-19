import rdflib

from ted_sws.master_data_registry.services.rdf_fragment_processor import get_rdf_fragment_by_cet_uri_from_string, \
    get_rdf_fragments_by_cet_uri_from_file


def test_get_rdf_fragment_by_cet_uri_from_string(rdf_content, organisation_cet_uri):
    rdf_fragments = get_rdf_fragment_by_cet_uri_from_string(rdf_content=rdf_content, cet_uri=organisation_cet_uri)
    assert len(rdf_fragments) == 3
    for rdf_fragment in rdf_fragments:
        assert type(rdf_fragment) == rdflib.Graph


def test_get_rdf_fragments_by_cet_uri_from_file(rdf_file_path, organisation_cet_uri):
    rdf_fragments = get_rdf_fragments_by_cet_uri_from_file(rdf_file_path=rdf_file_path, cet_uri=organisation_cet_uri)
    assert len(rdf_fragments) == 3
    for rdf_fragment in rdf_fragments:
        assert type(rdf_fragment) == rdflib.Graph
