from ted_sws.resources import get_mapping_json_file, get_mapping_csv_file

COUNTRIES_MAPPING_FILE = "countries.json"
FORM_TYPE_MAPPING_FILE = "form_type.json"
LANGUAGES_MAPPING_FILE = "languages.json"
LEGAL_BASIS_MAPPING_FILE = "legal_basis.json"
NOTICE_TYPE_MAPPING_FILE = "notice_type.json"
NUTS_CODES_MAPPING_FILE = "nuts.json"
STANDARD_FORMS_MAPPING_FILE = "sforms_mapping.csv"
E_FORMS_FORMS_MAPPING_FILE = "eforms_mapping.csv"
FILTER_MAPPING_FILE = "df_filter_map.csv"


class MappingFilesRegistry:
    """
     Registry of mapping files. This will return the specific file content
    """

    @property
    def countries(self):
        return get_mapping_json_file(COUNTRIES_MAPPING_FILE)

    @property
    def form_type(self):
        return get_mapping_json_file(FORM_TYPE_MAPPING_FILE)

    @property
    def languages(self):
        return get_mapping_json_file(LANGUAGES_MAPPING_FILE)

    @property
    def legal_basis(self):
        return get_mapping_json_file(LEGAL_BASIS_MAPPING_FILE)

    @property
    def notice_type(self):
        return get_mapping_json_file(NOTICE_TYPE_MAPPING_FILE)

    @property
    def nuts(self):
        return get_mapping_json_file(NUTS_CODES_MAPPING_FILE)

    @property
    def sf_notice_df(self):
        return get_mapping_csv_file(STANDARD_FORMS_MAPPING_FILE)

    @property
    def ef_notice_df(self):
        return get_mapping_csv_file(E_FORMS_FORMS_MAPPING_FILE)

    @property
    def filter_map_df(self):
        return get_mapping_csv_file(FILTER_MAPPING_FILE)
