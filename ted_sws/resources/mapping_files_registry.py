from ted_sws.resources import get_mapping_json_file, get_mapping_csv_file


class MappingFilesRegistry:
    """
     Registry of mapping files. This will return the specific file content
    """
    @property
    def countries(self):
        return get_mapping_json_file("countries.json")

    @property
    def form_type(self):
        return get_mapping_json_file("form_type.json")

    @property
    def languages(self):
        return get_mapping_json_file("languages.json")

    @property
    def legal_basis(self):
        return get_mapping_json_file("legal_basis.json")

    @property
    def notice_type(self):
        return get_mapping_json_file("notice_type.json")

    @property
    def nuts(self):
        return get_mapping_json_file("nuts.json")

    @property
    def sf_notice_df(self):
        return get_mapping_csv_file("sforms_mapping.csv")

    @property
    def ef_notice_df(self):
        return get_mapping_csv_file("eforms_mapping.csv")

    @property
    def filter_map_df(self):
        return get_mapping_csv_file("df_filter_map.csv")
