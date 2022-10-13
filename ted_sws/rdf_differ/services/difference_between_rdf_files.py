from typing import List

import rdflib
from rdflib import Graph
from rdflib.compare import isomorphic, graph_diff


def generate_rdf_differ_html_report(first_rml_file: str, second_rml_file: str):
    """
    Given two RML files representing turtle-encoded RDF,
    check whether they represent the same graph.
    """
    first_graph = Graph().parse(first_rml_file, format='turtle')
    second_graph = Graph().parse(second_rml_file, format='turtle')
    is_equal_graph = isomorphic(first_graph, second_graph)
    if not is_equal_graph:
        _, first, second = graph_diff(first_graph, second_graph)
        html_differences_report = f'''
                <html>
                    <head>
                        <title>{'differences between rdf files'}</title>
                    </head>
                    <body>
                        <h1>{{difference in the first file}}</h1>
                        <p>{first.serialize(format="nt")}</p>
                        <h2>{{difference in the second file}}</h2>
                        <p>{second.serialize(format="nt")}</p>
                    </body>'''
    return html_differences_report

