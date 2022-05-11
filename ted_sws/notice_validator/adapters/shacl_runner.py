import rdflib
from pyshacl import validate

from ted_sws.core.model.transform import FileResource

TURTLE_FILE_TYPE = "turtle"
SHACL_FILE_FORMAT_TURTLE = "n3"


class SHACLRunner:
    """
        Runs SHACL shape against a rdf file and return the execution results
    """

    def __init__(self, rdf_content: str):
        self.rdf_graph = rdflib.Graph().parse(data=rdf_content)

    @classmethod
    def _get_file_format(cls, file_name: str):
        """
        Looking at the file extension return the file format type (XML or Turtle)
        :param file_name:
        :return:
        """
        file_type = rdflib.util.guess_format(file_name)
        return SHACL_FILE_FORMAT_TURTLE if file_type == TURTLE_FILE_TYPE else file_type

    def validate(self, shacl_shape_files: [FileResource]) -> tuple:
        """
        Validates with a list of shacl shape files and return one validation result
        :param shacl_shape_files:
        :return:
        """
        shacl_shape_graph = rdflib.Graph()
        for shacl_shape_file in shacl_shape_files:
            shacl_shape_graph.parse(data=shacl_shape_file.file_content,
                                    format=self._get_file_format(file_name=shacl_shape_file.file_name))
        validation_result = validate(self.rdf_graph,
                                     shacl_graph=shacl_shape_graph,
                                     meta_shacl=False,
                                     js=False,
                                     debug=False)
        return validation_result
