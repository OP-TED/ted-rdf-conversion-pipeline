import pathlib
from typing import List, Protocol

from pydantic import BaseModel


class LimesDataSource(BaseModel):
    """
        This class provide a model for LIMES alignment engine data source.
    """
    id: str
    sparql_endpoint: str
    sparql_variable: str
    sparql_restrictions: List[str]
    sparql_properties: List[str]


class LimesDataResult(BaseModel):
    """
        This class provide a model for LIMES alignment engine result.
    """
    threshold: float
    result_file_path: str
    relation: str


class LimesConfigParams(BaseModel):
    """
        This class provide a model for LIMES alignment engine configurations.
    """
    prefixes: dict
    source: LimesDataSource
    target: LimesDataSource
    alignment_metric: str
    acceptance: LimesDataResult
    review: LimesDataResult
    result_file_format: str


class LimesConfigGenerator(Protocol):
    """
        This class provide a model for LimesConfigGenerators functions.
    """
    def __call__(self, source_sparql_endpoint: str,
                 target_sparql_endpoint: str,
                 result_dir_path: pathlib.Path) -> LimesConfigParams:
        """
            This method define a signature for a LimesConfigGenerator function.
        """
