from typing import List

from pydantic import BaseModel

from ted_sws import config

DEFAULT_PREFIXES = config.SPARQL_PREFIXES
DEFAULT_RESULT_FILE_FORMAT = "TTL"
DEFAULT_RELATION = "owl:sameAs"


class DataSource(BaseModel):
    id: str = "undefined_id"
    sparql_endpoint: str
    sparql_variable: str
    sparql_restrictions: List[str] = []
    sparql_properties: List[str] = []


class DataResult(BaseModel):
    threshold: float
    file_name: str
    relation: str = DEFAULT_RELATION


class LimesConfigParams(BaseModel):
    prefixes: dict = DEFAULT_PREFIXES
    source: DataSource
    target: DataSource
    alignment_metric: str
    acceptance: DataResult
    review: DataResult
    result_file_format: str = DEFAULT_RESULT_FILE_FORMAT
