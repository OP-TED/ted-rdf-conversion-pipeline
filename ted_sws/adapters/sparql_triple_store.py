#!/usr/bin/python3

# minio_feature_store.py
# Date:  21.07.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

import io
from pathlib import Path
from abc import ABC, abstractmethod
from SPARQLWrapper import SPARQLWrapper, CSV, JSON

import pandas as pd

from string import Template

DEFAULT_ENCODING = 'utf-8'
DEFAULT_ENDPOINT_URL = "https://publications.europa.eu/webapi/rdf/sparql"


class SubstitutionTemplate(Template):
    delimiter = '~'


class SPARQLClientPool(object):
    """
        A singleton connection pool, that hosts a dictionary of endpoint_urls and
        a corresponding SPARQLWrapper object connecting to it.
        The rationale of this connection pool is to reuse connection objects and save time.
    """
    connection_pool = {}

    @staticmethod
    def create_or_reuse_connection(endpoint_url: str):
        if endpoint_url not in SPARQLClientPool.connection_pool:
            SPARQLClientPool.connection_pool[endpoint_url] = SPARQLWrapper(endpoint_url)
        return SPARQLClientPool.connection_pool[endpoint_url]


class TripleStoreABC(ABC):
    """
        This class provides an abstraction for a TripleStore.
    """

    @abstractmethod
    def with_query(self, sparql_query: str, substitution_variables: dict = None,
                   sparql_prefixes: str = "") -> 'TripleStoreABC':
        """
            This method will take a query in a string format
        :param sparql_query:
        :param substitution_variables:
        :param sparql_prefixes:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def with_query_from_file(self, sparql_query_file_path: str, substitution_variables: dict = None,
                             prefixes: str = "") -> 'TripleStoreABC':
        """
            This method will read a query from a file
        :param sparql_query_file_path:
        :param substitution_variables:
        :param prefixes:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def fetch_tabular(self) -> pd.DataFrame:
        """
            This method will return the result of the SPARQL query in a tabular format (dataframe)
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def fetch_tree(self) -> dict:
        """
            This method will return the result of the SPARQL query in a dict format (json)
        :return:
        """
        raise NotImplementedError


class SPARQLTripleStore(TripleStoreABC):

    def __init__(self, endpoint_url: str = DEFAULT_ENDPOINT_URL):
        self.endpoint = SPARQLClientPool.create_or_reuse_connection(endpoint_url)

    def with_query(self, sparql_query: str, substitution_variables: dict = None,
                   sparql_prefixes: str = "") -> TripleStoreABC:
        """
            Set the query text and return the reference to self for chaining.
        :return:
        """
        if substitution_variables:
            template_query = SubstitutionTemplate(sparql_query)
            sparql_query = template_query.safe_substitute(substitution_variables)

        new_query = (sparql_prefixes + " " + sparql_query).strip()

        self.endpoint.setQuery(new_query)
        return self

    def with_query_from_file(self, sparql_query_file_path: str, substitution_variables: dict = None,
                             prefixes: str = "") -> TripleStoreABC:
        """
            Set the query text and return the reference to self for chaining.
        :return:
        """

        with open(Path(sparql_query_file_path).resolve(), 'r') as file:
            query_from_file = file.read()

        if substitution_variables:
            template_query = SubstitutionTemplate(query_from_file)
            query_from_file = template_query.safe_substitute(substitution_variables)

        new_query = (prefixes + " " + query_from_file).strip()

        self.endpoint.setQuery(new_query)
        return self

    def fetch_tabular(self) -> pd.DataFrame:
        """
        Get query results in a tabular format
        :return:
        """
        if not self.endpoint.queryString or self.endpoint.queryString.isspace():
            raise Exception("The query is empty.")

        self.endpoint.setReturnFormat(CSV)
        query_result = self.endpoint.queryAndConvert()
        return pd.read_csv(io.StringIO(str(query_result, encoding=DEFAULT_ENCODING)))

    def fetch_tree(self):
        """
        Get query results in a dict format
        :return:
        """
        if not self.endpoint.queryString or self.endpoint.queryString.isspace():
            raise Exception("The query is empty.")

        self.endpoint.setReturnFormat(JSON)
        return self.endpoint.queryAndConvert()

    def __str__(self):
        return f"from <...{str(self.endpoint.endpoint)[-30:]}> {str(self.endpoint.queryString)[:60]} ..."
