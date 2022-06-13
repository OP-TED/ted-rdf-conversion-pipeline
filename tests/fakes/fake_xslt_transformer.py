import pathlib

from ted_sws.core.adapters.xml_preprocessor import XMLPreprocessorABC


class FakeXSLTTransformer(XMLPreprocessorABC):
    def transform_with_xslt_to_string(self, xslt_path: pathlib.Path, xml_path: pathlib.Path) -> str:
        return "transform_with_xslt_to_string"

    def transform_with_xslt_to_file(self, result_file_path: pathlib.Path, xslt_path: pathlib.Path,
                                    xml_path: pathlib.Path):
        return "transform_with_xslt_to_file"
