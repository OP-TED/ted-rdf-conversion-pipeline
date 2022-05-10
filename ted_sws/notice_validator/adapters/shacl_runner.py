import rdflib
from pyshacl import validate


class SHACLRunner:
    """
        Runs SHACL shapes against a rdf file and return the execution results
    """

    def __init__(self, rdf_content: str):
        self.rdf_graph = rdflib.Graph().parse(data=rdf_content)

    def validate(self, shacl_shape_content: str, shacl_shape_file_format: str = "xml") -> tuple:
        shacl_shape_graph = rdflib.Graph().parse(data=shacl_shape_content, format=shacl_shape_file_format)
        validation_result = validate(self.rdf_graph,
                                     shacl_graph=shacl_shape_graph,
                                     # inference='rdfs',
                                     meta_shacl=False,
                                     js=False,
                                     debug=False)
        return validation_result
