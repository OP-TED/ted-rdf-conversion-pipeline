from typing import List

from pydantic import BaseModel


class DataSource(BaseModel):
    id: str
    sparql_endpoint: str
    sparql_variable: str
    sparql_restrictions: List[str]
    sparql_properties: List[str]


class DataResult(BaseModel):
    threshold: float
    result_file_path: str
    relation: str


class LimesConfigParams(BaseModel):
    prefixes: dict
    source: DataSource
    target: DataSource
    alignment_metric: str
    acceptance: DataResult
    review: DataResult
    result_file_format: str
