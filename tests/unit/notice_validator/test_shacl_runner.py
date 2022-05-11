import rdflib

from ted_sws.notice_validator.adapters.shacl_runner import SHACLRunner


def test_shacl_runner(rdf_file_content, list_of_shacl_files):
    shacl_runner = SHACLRunner(rdf_content=rdf_file_content)
    result = shacl_runner.validate(shacl_shape_files=list_of_shacl_files)

    assert isinstance(result, tuple)
    conforms, result_graph, results_text = result
    assert conforms is False
    assert isinstance(result_graph, rdflib.Graph)
    assert isinstance(results_text, str)
