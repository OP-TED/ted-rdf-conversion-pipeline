from ted_sws.rml_to_html.resources import get_sparql_query


class QueryRegistry:

    @property
    def TRIPLE_MAP(self):
        return get_sparql_query(query_file_name="get_triple_maps.rq")

    @property
    def LOGICAL_SOURCE(self):
        return get_sparql_query(query_file_name="get_logical_source.rq")

    @property
    def SUBJECT_MAP(self):
        return get_sparql_query(query_file_name="get_subject_map.rq")

    @property
    def PREDICATE_OBJECT_MAP(self):
        return get_sparql_query(query_file_name="get_predicate_object_map.rq")
