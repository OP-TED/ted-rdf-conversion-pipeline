from rdflib import Graph
import networkx as nx
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph
from pathlib import Path


def detect_graph_components(file_path: Path):
    """
        Given a notice .ttl file, detect if notice as graph is connected, else printing connected components without
        the larges one.
    :param file_path: Path to notice file
    """
    rdf_graph = Graph().parse(file_path, format="turtle")
    networkx_graph = rdflib_to_networkx_graph(rdf_graph)
    result = ''
    if nx.is_connected(networkx_graph):
        result += f"Graph {file_path.name} is fully connected."
    else:
        result += f"Graph {file_path.name} is not fully connected. Printing connected components, with the exception " \
                  f"of the largest one.\n "
        graph_components = list(nx.connected_components(networkx_graph))
        graph_components.pop(0)
        for i, elem in enumerate(graph_components):
            result += "-"*40+f"Component nr {i+1}"+"-"*40+"\n"
            result += '\n'.join(elem)
            result += "\n"+"-"*40+f"End component nr {i+1}"+"-"*40
    return result
