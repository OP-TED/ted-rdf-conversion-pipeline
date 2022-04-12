import pathlib
from tempfile import NamedTemporaryFile

from ted_sws.mapping_suite_processor.adapters.yarrrml2rml_convertor import YARRRML2RMLConvertor


def test_yarrrml_to_rml_convertor(yarrrml_file_content, rml_file_result):

    yarrrml_file = NamedTemporaryFile(mode="w",suffix=".yaml")
    rml_file = NamedTemporaryFile(mode="w+")
    yarrrml_file_path = pathlib.Path(yarrrml_file.name)
    rml_file_path = pathlib.Path(rml_file.name)
    yarrrml_file.write(yarrrml_file_content)
    yarrrml2rml_convertor = YARRRML2RMLConvertor()
    print(yarrrml_file_path.name)
    yarrrml2rml_convertor.convert(yarrrml_input_file_path = yarrrml_file_path,
                                  rml_output_file_path= rml_file_path
                                  )
    rml_result = rml_file.read()
    print(rml_result)
    #print(yarrrml_file_content)