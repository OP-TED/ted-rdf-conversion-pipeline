from ted_sws.rml_to_html.resources import get_sparql_query


class QueryRegistry:

    @property
    def TRIPLE_MAP(self):
        return get_sparql_query(query_file_name="get_triple_maps.rq")