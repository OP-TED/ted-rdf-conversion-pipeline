from typing import List

import rdflib
from rdflib import Graph
from rdflib.compare import isomorphic, graph_diff

from tests import TEST_DATA_PATH

FIRST_RML_FILE = TEST_DATA_PATH / "technical_mapping_F03.rml.ttl"
SECOND_RML_FILE = TEST_DATA_PATH / "technical_mapping_F06.rml.ttl"


def rdf_differ_service(FIRST_RML_FILE: str, SECOND_RML_FILE: str):
    """
    Given two RML files representing turtle-encoded RDF,
    check whether they represent the same graph.
    """
    first_grath = Graph().parse(FIRST_RML_FILE, format='turtle')
    second_grath = Graph().parse(SECOND_RML_FILE, format='turtle')
    eq = isomorphic(first_grath, second_grath)
    if not eq:
        _, first, second = graph_diff(first_grath, second_grath)
        html_report = f'''
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
        rezult = open('differences_between_files.html', 'w')
        rezult.write(html_report)
        rezult.close()
    return rezult

