import codecs

import rdflib
from rdflib import Graph, RDF
from rdflib.compare import isomorphic, graph_diff
from bs4 import BeautifulSoup
from ted_sws.rdf_differ.services.difference_between_rdf_files import rdf_differ_service


def test_rdf_differ_service(first_rml_file, second_rml_file):
    differences_between_files = rdf_differ_service(first_rml_file, second_rml_file)
    file = open(f"{differences_between_files.name}", "r", encoding='utf-8')
    assert len(file.read()) > 10





