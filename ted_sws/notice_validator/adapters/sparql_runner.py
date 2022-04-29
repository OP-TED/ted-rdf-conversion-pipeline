import rdflib


class SPARQLRunner:
    """
        Runs a SPARQL query against a rdf file and return the query result
    """
    def __init__(self, rdf_content: str):
        self.graph = rdflib.Graph()
        self.graph.parse(data=rdf_content)

    def query(self, query_object: str):
        return self.graph.query(query_object)
