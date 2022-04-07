from ted_sws.core.adapters.xml_preprocessor import XMLPreprocessor


def test_xml_processor(path_to_test_xml_file, path_to_test_xslt_file, tmp_path):
    xslt_transformer = XMLPreprocessor()

    result = xslt_transformer.transform_with_xslt_to_string(xml_path=path_to_test_xml_file,
                                                            xslt_path=path_to_test_xslt_file)
    assert isinstance(result, str)
    assert "Bob Dylan" in result

    path_to_result_file = tmp_path / "result.xml"
    xslt_transformer.transform_with_xslt_to_file(result_file_path=path_to_result_file, xml_path=path_to_test_xml_file,
                                                 xslt_path=path_to_test_xslt_file)

    assert path_to_result_file.is_file()
    with open(path_to_result_file) as file:
        assert "Bob Dylan" in file.read()
