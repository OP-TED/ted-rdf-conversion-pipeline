from rdflib import Graph, RDF
from ted_sws.rdf_differ.services.difference_between_rdf_files import generate_rdf_differ_html_report

CONTENT_FIRST_FILE = '<h1>{difference in the first file}</h1>'
CONTENT_SECOND_FILE = '<h2>{difference in the second file}</h2>'


def test_generate_rdf_differ_html_report(technical_mapping_f03_file_path, technical_mapping_f06_file_path):
    differences_between_files = generate_rdf_differ_html_report(technical_mapping_f03_file_path, technical_mapping_f06_file_path)
    assert CONTENT_FIRST_FILE in differences_between_files
    assert CONTENT_SECOND_FILE in differences_between_files
    assert len(differences_between_files) > 10







