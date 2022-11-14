from pathlib import Path

import networkx as nx
from rdflib import Graph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph

NR_OF_LINE_SEPARATORS = 40


def detect_graph_components(file_path: Path) -> str:
    """
        Given a rdf file path (.ttl), detect if notice as graph is connected, else printing connected components without
        the larges one.
    :param file_path: Path to notice file
    """
    rdf_graph = Graph().parse(file_path, format="turtle")
    networkx_graph = rdflib_to_networkx_graph(rdf_graph)
    result_log = ''
    if nx.is_connected(networkx_graph):
        result_log += f"Graph {file_path.name} is fully connected."
    else:
        result_log += f"Graph {file_path.name} is not fully connected. Printing connected components, with the " \
                      f"exception of the largest one.\n "
        graph_components = list(nx.connected_components(networkx_graph))
        graph_components.pop(0)
        for i, elem in enumerate(graph_components):
            result_log += "-" * NR_OF_LINE_SEPARATORS + f"Component nr {i + 1}" + "-" * NR_OF_LINE_SEPARATORS + "\n"
            result_log += '\n'.join(elem)
            result_log += "\n" + "-" * NR_OF_LINE_SEPARATORS + f"End component nr {i + 1}" + \
                          "-" * NR_OF_LINE_SEPARATORS + "\n"
    return result_log
