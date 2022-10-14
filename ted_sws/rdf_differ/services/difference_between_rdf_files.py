from rdflib import Graph
from rdflib.compare import isomorphic, graph_diff
import html


def generate_rdf_differ_html_report(first_rml_file: str, second_rml_file: str) -> str:
    """
    Given two RML files representing turtle-encoded RDF,
    check whether they represent the same graph.
    """
    first_graph = Graph().parse(first_rml_file, format='turtle')
    second_graph = Graph().parse(second_rml_file, format='turtle')
    is_equal_graph = isomorphic(first_graph, second_graph)
    html_differences_report = f'''
                <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="utf-8">
                        <title>Differences between rdf files</title>
                    </head>
                    <body>
                        <h1>Differences between rdf files</h1>
                        <hr>
                        '''
    if not is_equal_graph:
        in_both, in_first, in_second = graph_diff(first_graph, second_graph)
        html_differences_report += "<h2>Difference in the first file</h2>"
        html_differences_report += f"<h5>{first_rml_file}</h5>"
        html_differences_report += "<ul>"
        for line in in_first.serialize(format='nt', encoding="utf-8").splitlines():
            if line:
                html_differences_report += f"<li>{html.escape(line.decode('utf-8'))}</li>"
        html_differences_report += "</ul>"
        html_differences_report += "<ul>"
        html_differences_report += "<h2>Difference in the second file</h2>"
        html_differences_report += f"<h5>{second_rml_file}</h5>"
        html_differences_report += "<hr>"
        for line in in_second.serialize(format='nt', encoding="utf-8").splitlines():
            if line:
                html_differences_report += f"<li>{html.escape(line.decode('utf-8'))}</li>"
        html_differences_report += "</ul>"
        html_differences_report += "<hr>"
    html_differences_report += "</body></html>"
    return html_differences_report
