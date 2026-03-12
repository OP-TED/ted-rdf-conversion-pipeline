DEFAULT_DATE_STRING_FIELDS_SUFFIX_MAP = {"_str_y": "%Y",
                                         "_str_ym": "%Y-%m",
                                         "_str_ymd": "%Y-%m-%d"}


def inject_date_string_fields(data: dict, date_field_name: str, date_string_fields_suffix_map: dict = None):
    """
        This function adds supplementary date string fields with different formats.
    :param data:
    :param date_field_name:
    :param date_string_fields_suffix_map:
    :return:
    """
    if date_string_fields_suffix_map is None:
        date_string_fields_suffix_map = DEFAULT_DATE_STRING_FIELDS_SUFFIX_MAP
    for date_field_suffix, date_string_format in date_string_fields_suffix_map.items():
        data[date_field_name + date_field_suffix] = data[date_field_name].strftime(date_string_format)


def remove_date_string_fields(data: dict, date_field_name: str, date_string_fields_suffix_map: dict = None):
    """
        This function remove supplementary date string fields.
    :param data:
    :param date_field_name:
    :param date_string_fields_suffix_map:
    :return:
    """
    if date_string_fields_suffix_map is None:
        date_string_fields_suffix_map = DEFAULT_DATE_STRING_FIELDS_SUFFIX_MAP
    for date_field_suffix in date_string_fields_suffix_map.keys():
        data.pop(date_field_name + date_field_suffix, None)
