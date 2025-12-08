import rdflib

from ted_sws.core.model.transform import FileResource


# TODO to refactor this to accept only a list of file resorces and move it to core adapters

class SPARQLRunner:
    """
        Runs a SPARQL query against a rdf file and return the query result
    """

    def __init__(self, rdf_content: str = None, files: [FileResource] = None):
        self.graph = rdflib.Graph()
        self.rdf_content = rdf_content
        self.files = files

    def _load_data_into_graph(self):
        if self.rdf_content:
            self.graph.parse(data=self.rdf_content)
        else:
            for file in self.files:
                self.graph.parse(data=file.file_content)

    def query(self, query_object: str):
        self._load_data_into_graph()
        return self.graph.query(query_object)
