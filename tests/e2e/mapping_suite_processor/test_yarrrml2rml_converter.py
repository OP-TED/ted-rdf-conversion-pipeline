import os
import pathlib
from tempfile import NamedTemporaryFile

from ted_sws.mapping_suite_processor.adapters.yarrrml2rml_converter import YARRRML2RMLConverter


def test_yarrrml_to_rml_convertor(yarrrml_file_content, rml_file_result):
    yarrrml_file = NamedTemporaryFile(mode="w+",suffix=".yaml")
    rml_file = NamedTemporaryFile(mode="w+")
    yarrrml_file_path = pathlib.Path(yarrrml_file.name)
    rml_file_path = pathlib.Path(rml_file.name)
    yarrrml_file.write(yarrrml_file_content)
    yarrrml_file.seek(0, os.SEEK_SET)
    yarrrml2rml_converter = YARRRML2RMLConverter()
    yarrrml2rml_converter.convert(yarrrml_input_file_path = yarrrml_file_path,
                                  rml_output_file_path= rml_file_path
                                  )
    rml_result = rml_file.read()
    assert rml_result == rml_file_result
