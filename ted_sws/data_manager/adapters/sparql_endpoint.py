#!/usr/bin/python3

# minio_feature_store.py
# Date:  21.07.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

import io
import json
import pathlib
from abc import ABC, abstractmethod
from pathlib import Path
from string import Template

import pandas as pd
import rdflib
from SPARQLWrapper import SPARQLWrapper, CSV, JSON, RDF

from ted_sws import config

DEFAULT_ENCODING = 'utf-8'
DEFAULT_RDF_FILE_FORMAT = "n3"


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
    def create_or_reuse_connection(endpoint_url: str, user: str, password: str):
        if endpoint_url not in SPARQLClientPool.connection_pool:
            sparql_wrapper = SPARQLWrapper(endpoint_url)
            sparql_wrapper.setCredentials(
                user=user,
                passwd=password
            )
            SPARQLClientPool.connection_pool[endpoint_url] = sparql_wrapper
        return SPARQLClientPool.connection_pool[endpoint_url]


class TripleStoreEndpointABC(ABC):
    """
        This class provides an abstraction for a TripleStore.
    """

    def with_query(self, sparql_query: str, substitution_variables: dict = None,
                   sparql_prefixes: str = "") -> 'TripleStoreEndpointABC':
        """
            This method will take a query in a string format
        :param sparql_query:
        :param substitution_variables:
        :param sparql_prefixes:
        :return:
        """
        if substitution_variables:
            template_query = SubstitutionTemplate(sparql_query)
            sparql_query = template_query.safe_substitute(substitution_variables)

        sparql_query = (sparql_prefixes + " " + sparql_query).strip()
        self._set_sparql_query(sparql_query=sparql_query)
        return self

    def with_query_from_file(self, sparql_query_file_path: str, substitution_variables: dict = None,
                             sparql_prefixes: str = "") -> 'TripleStoreEndpointABC':
        """
            This method will read a query from a file
        :param sparql_query_file_path:
        :param substitution_variables:
        :param sparql_prefixes:
        :return:
        """
        sparql_query = Path(sparql_query_file_path).resolve().read_text(encoding="utf-8")
        return self.with_query(sparql_query=sparql_query, substitution_variables=substitution_variables,
                               sparql_prefixes=sparql_prefixes)

    @abstractmethod
    def _set_sparql_query(self, sparql_query: str):
        """
            This method is used to set sparql query for future query operation.
        :param sparql_query:
        :return:
        """

    @abstractmethod
    def fetch_tabular(self) -> pd.DataFrame:
        """
            This method will return the result of the SPARQL query in a tabular format (dataframe)
        :return:
        """

    @abstractmethod
    def fetch_tree(self) -> dict:
        """
            This method will return the result of the SPARQL query in a dict format (json)
        :return:
        """

    @abstractmethod
    def fetch_rdf(self) -> rdflib.Graph:
        """
            This method will return the result of the SPARQL query in a RDF format,
            use this method only for SPARQL queries of type CONSTRUCT.
        :return:
        """

    def add_data_to_repository(self, file_content, repository_name, mime_type):
        pass


class SPARQLTripleStoreEndpoint(TripleStoreEndpointABC):

    def __init__(self, endpoint_url: str, user: str = None, password: str = None):
        user = user if user else config.AGRAPH_SUPER_USER
        password = password if password else config.AGRAPH_SUPER_PASSWORD
        self.endpoint = SPARQLClientPool.create_or_reuse_connection(endpoint_url, user, password)

    def _set_sparql_query(self, sparql_query: str):
        """
            This method is used to set sparql query for future query operation.
        :param sparql_query:
        :return:
        """
        self.endpoint.setQuery(sparql_query)

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

    def fetch_rdf(self) -> rdflib.Graph:
        """
            This method will return the result of the SPARQL query in a RDF format,
            use this method only for SPARQL queries of type CONSTRUCT or DESCRIBE.
        :return:
        """
        return self.endpoint.queryAndConvert()

    def __str__(self):
        return f"from <...{str(self.endpoint.endpoint)[-30:]}> {str(self.endpoint.queryString)[:60]} ..."


class SPARQLStringEndpoint(TripleStoreEndpointABC):
    """
        This class is specialized to query an RDF string content using SPARQL queries.
    """

    def __init__(self, rdf_content: str, rdf_content_format: str = DEFAULT_RDF_FILE_FORMAT):
        self.graph = rdflib.Graph()
        self.graph.parse(data=rdf_content, format=rdf_content_format)
        self.sparql_query = None

    def _set_sparql_query(self, sparql_query: str):
        """
            This method is used to set sparql query for future query operation.
        :param sparql_query:
        :return:
        """
        self.sparql_query = sparql_query

    def fetch_tabular(self) -> pd.DataFrame:
        """
        Get query results in a tabular format
        :return:
        """
        query_result = self.graph.query(query_object=self.sparql_query)
        return pd.DataFrame(data=query_result, columns=[str(var) for var in query_result.vars])

    def fetch_tree(self) -> dict:
        """
        Get query results in a dict format
        :return:
        """
        query_result = self.graph.query(query_object=self.sparql_query)
        return json.loads(query_result.serialize(format="json"))

    def fetch_rdf(self) -> rdflib.Graph:
        """
            This method will return the result of the SPARQL query in a RDF format,
            use this method only for SPARQL queries of type CONSTRUCT or DESCRIBE.
        :return:
        """
        query_result = self.graph.query(query_object=self.sparql_query)
        if query_result.type in ("CONSTRUCT", "DESCRIBE"):
            return query_result.graph
        else:
            raise Exception("Fetch RDF method work only with CONSTRUCT and DESCRIBE sparql queries!")


class SPARQLFileEndpoint(SPARQLStringEndpoint):
    """
        This class is specialized to query an RDF file using SPARQL queries.
    """

    def __init__(self, rdf_file_path: pathlib.Path):
        rdf_content = rdf_file_path.read_text(encoding="utf-8")
        super().__init__(rdf_content)
