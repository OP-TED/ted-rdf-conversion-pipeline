try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

import ted_sws.rml_to_html.resources.queries


def get_sparql_query(query_file_name: str) -> str:
    """
        get a predefined SPARQL query by reference to file name
    """
    with pkg_resources.path(queries, query_file_name) as path:
        return path.read_text()
