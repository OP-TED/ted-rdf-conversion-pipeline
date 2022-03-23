from ted_sws.metadata_normaliser.resources import get_mapping_file


class MappingFilesRegistry:
    """
     Registry of mapping files. This will return the specific file content
    """
    @property
    def countries(self):
        return get_mapping_file("countries.json")

    @property
    def form_type(self):
        return get_mapping_file("form_type.json")

    @property
    def languages(self):
        return get_mapping_file("languages.json")

    @property
    def legal_basis(self):
        return get_mapping_file("legal_basis.json")

    @property
    def notice_type(self):
        return get_mapping_file("notice_type.json")

    @property
    def nuts(self):
        return get_mapping_file("nuts.json")

