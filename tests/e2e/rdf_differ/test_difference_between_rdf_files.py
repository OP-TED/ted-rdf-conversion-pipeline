from ted_sws.rdf_differ.services.difference_between_rdf_files import rdf_differ_service


def test_rdf_differ_service(first_rml_file, second_rml_file):
    rdf_differ_service(first_rml_file, second_rml_file)
    assert first_rml_file != second_rml_file



