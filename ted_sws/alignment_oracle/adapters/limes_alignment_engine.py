import abc
import pathlib
from typing import List

from jinja2 import Environment, PackageLoader
from pydantic import BaseModel

TEMPLATES = Environment(loader=PackageLoader("ted_sws.alignment_oracle.resources", "templates"))
LIMES_CONFIG_TEMPLATE = "limes_config.jinja2"


class DataSource(BaseModel):
    id: str = ""
    sparql_endpoint: str = ""
    sparql_variable: str = ""
    sparql_restrictions: List[str] = []
    sparql_properties: List[str] = []


class DataResult(BaseModel):
    threshold: float = 0.5
    file_name: str = ""
    relation: str = ""


class LimesConfigParams(BaseModel):
    prefixes: dict = {}
    source: DataSource
    target: DataSource
    alignment_metric: str = ""
    acceptance: DataResult
    review: DataResult
    result_file_format: str = ""


def test_function():
    limes_config_params = LimesConfigParams(source=DataSource(),
                                            target=DataSource(),
                                            acceptance=DataResult(),
                                            review=DataResult()).dict()
    print(TEMPLATES.get_template(LIMES_CONFIG_TEMPLATE).render(limes_config_params))


class LimesDataSourceConfigurator:

    def __init__(self, data_source_config: DataSource, caller: 'LimesAlignmentEngineConfigBuilder'):
        self.caller = caller
        self.data_source_config = data_source_config

    def save_configs(self) -> 'LimesAlignmentEngineConfigBuilder':
        return self.caller


class LimesAlignmentEngineConfigBuilder:
    def __init__(self, prefixes: dict = None):
        self.prefixes = prefixes if prefixes else {}
        self.source = DataSource()
        self.target = DataSource()
        self.result_file_format = "NT"
        self.alignment_metric = ""

    def set_prefixes(self, prefixes: dict) -> 'LimesAlignmentEngineConfigBuilder':
        self.prefixes = prefixes
        return self

    def add_prefixes(self, prefixes: dict) -> 'LimesAlignmentEngineConfigBuilder':
        self.prefixes.update(prefixes)
        return self

    def set_result_file_format(self, result_file_format: str) -> 'LimesAlignmentEngineConfigBuilder':
        self.result_file_format = result_file_format
        return self

    def set_alignment_metric(self, alignment_metric: str) -> 'LimesAlignmentEngineConfigBuilder':
        self.alignment_metric = alignment_metric
        return self

    def source_configurator(self) -> LimesDataSourceConfigurator:
        return LimesDataSourceConfigurator()

    def build(self):
        ...


class LimesAlignmentEngine:

    def __init__(self, limes_executable_path: pathlib.Path):
        ...

    def execute(self, config_builder: LimesAlignmentEngineConfigBuilder):
        ...
