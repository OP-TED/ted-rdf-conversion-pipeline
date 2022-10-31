import abc
from json import loads
from pathlib import Path
from typing import List, Union
from urllib.parse import urljoin

import rdflib.util
import requests
from franz.openrdf.repository import Repository
from franz.openrdf.sail import AllegroGraphServer
from requests.auth import HTTPBasicAuth

from ted_sws import config
from ted_sws.data_manager.adapters.sparql_endpoint import TripleStoreEndpointABC, SPARQLTripleStoreEndpoint


FUSEKI_REPOSITORY_ALREADY_EXIST_ERROR_MSG = 'A repository with this name already exists.'

class TripleStoreABC:
    @abc.abstractmethod
    def create_repository(self, repository_name: str):
        """
        Method to create a repository
        :param repository_name:
        :return:
        """

    @abc.abstractmethod
    def delete_repository(self, repository_name: str):
        """
        Method to delete a repository
        :param repository_name:
        :return:
        """

    @abc.abstractmethod
    def list_repositories(self) -> List[str]:
        """
        Method to list all repositories
        :return:
        """

    @abc.abstractmethod
    def add_data_to_repository(self, file_content: Union[str, bytes, bytearray], mime_type: str, repository_name: str):
        """
        Method to add triples from a string
        :param file_content:
        :param repository_name:
        :param mime_type:
        :return:
        """

    @abc.abstractmethod
    def add_file_to_repository(self, file_path, repository_name):
        """
        Method to add triples from a file
        :param file_path:
        :param repository_name:
        :return:
        """

    def get_sparql_triple_store_endpoint(self, repository_name: str = None) -> TripleStoreEndpointABC:
        """
            Return a triple store SPARQL endpoint connection
        """


class AllegroGraphTripleStore(TripleStoreABC):
    """
        This class is handling interactions with Allegro Graph triple store
        Note: If catalog name is not set, every operation will be executed at root level in the triple store
    """

    def __init__(self, host: str, user: str, password: str, default_repository="default", catalog_name=None):
        self.host = host
        self.user = user
        self.password = password
        self.catalog_name = catalog_name
        self.default_repository = default_repository
        self.allegro = AllegroGraphServer(host=self.host,
                                          port=443,
                                          user=self.user,
                                          password=self.password,
                                          verifyhost=0,
                                          verifypeer=0)

    def create_repository(self, repository_name: str):
        """
        Method to create a repository
        :param repository_name:
        :return:
        """
        catalog = self.allegro.openCatalog(name=self.catalog_name)
        catalog.createRepository(name=repository_name)

    def delete_repository(self, repository_name: str):
        """
        Method to delete a repository
        :param repository_name:
        :return:
        """
        catalog = self.allegro.openCatalog(name=self.catalog_name)
        catalog.deleteRepository(name=repository_name)

    def _get_repository(self, repository_name: str) -> Repository:
        """
        Method to get a repository in order to execute operations on it
        :param repository_name:
        :return:
        """
        name = repository_name if repository_name else self.default_repository
        return self.allegro.openCatalog().getRepository(name=name, access_verb=Repository.ACCESS)

    def list_repositories(self):
        """
        Method to list all repositories
        :return:
        """
        return self.allegro.openCatalog(name=self.catalog_name).listRepositories()

    def add_data_to_repository(self, file_content: Union[str, bytes, bytearray], mime_type: str,
                               repository_name: str = None):
        """
        Method to add triples from a string
        :param file_content:
        :param repository_name:
        :param mime_type:
        :return:
        """

        repository = self._get_repository(repository_name=repository_name)
        repository.getConnection().addData(data=file_content)

    def add_file_to_repository(self, file_path, repository_name: str = None):
        """
        Method to add triples from a file
        :param file_path:
        :param repository_name:
        :return:
        """
        repository = self._get_repository(repository_name=repository_name)
        repository.getConnection().addFile(filePath=file_path)

    def get_sparql_triple_store_endpoint(self, repository_name: str = None) -> TripleStoreEndpointABC:
        """
            Return a triple store SPARQL endpoint connection
        """
        endpoint_url = f"{self.host}/repositories/{repository_name}"
        sparql_endpoint = SPARQLTripleStoreEndpoint(endpoint_url=endpoint_url)
        return sparql_endpoint


class FusekiException(Exception):
    """
        An exception when Fuseki server interaction has failed.
    """


RDF_MIME_TYPES = {
    "turtle": "text/turtle",
    "xml": "application/rdf+xml",
    "json-ld": "application/ld+json",
    "n3": "text/n3",
    "nt": "application/n-triples",
    "nquads": "application/n-quads",
    "trig": "application/trig",
}


class FusekiAdapter(TripleStoreABC):

    def __init__(self, host: str = config.FUSEKI_ADMIN_HOST,
                 user: str = config.FUSEKI_ADMIN_USER,
                 password: str = config.FUSEKI_ADMIN_PASSWORD):

        self.host = host
        self.user = user
        self.password = password

    def create_repository(self, repository_name: str):
        """
            Create the dataset for the Fuseki store
        :param repository_name: The repository identifier. This should be short alphanumeric string uniquely
        identifying the repository
        :return: true if repository was created
        """
        if not repository_name:
            raise ValueError('Repository name cannot be empty.')

        data = {
            'dbType': 'tdb',  # assuming that all repository are created persistent across restart
            'dbName': repository_name
        }

        response = requests.post(urljoin(self.host, f"/$/datasets"),
                                 auth=HTTPBasicAuth(self.user,
                                                    self.password),
                                 data=data)

        if response.status_code == 409:
            raise FusekiException(FUSEKI_REPOSITORY_ALREADY_EXIST_ERROR_MSG)

    def add_data_to_repository(self, file_content: Union[str, bytes, bytearray], mime_type: str, repository_name: str):
        url = urljoin(self.host, f"{repository_name}/data")
        headers = {
            "Content-Type": mime_type,
        }
        response = requests.post(url,
                                 auth=HTTPBasicAuth(self.user, self.password),
                                 data=file_content, headers=headers)
        if response.status_code != 200:
            raise FusekiException(f'Server refused to load the content with code {response.status_code}.')

    def add_file_to_repository(self, file_path: Path, repository_name: str):
        file_content = file_path.open('rb').read()
        file_format = rdflib.util.guess_format(str(file_path))
        mime_type = RDF_MIME_TYPES[file_format] if file_format in RDF_MIME_TYPES else "text/n3"
        self.add_data_to_repository(file_content=file_content, mime_type=mime_type, repository_name=repository_name)

    def delete_repository(self, repository_name: str):
        """
            Delete the repository from the Fuseki store
        :param repository_name: The repository identifier. This should be short alphanumeric string uniquely
        identifying the repository
        :return: true if repository was deleted
        """
        response = requests.delete(urljoin(self.host, f"/$/datasets/{repository_name}"),
                                   auth=HTTPBasicAuth(self.user,
                                                      self.password))

        if response.status_code == 404:
            raise FusekiException('The repository doesn\'t exist.')

    def list_repositories(self) -> list:
        """
            Get the list of the repository names from the Fuseki store.
        :return: the list of the repository names
        :rtype: list
        """
        response = requests.get(urljoin(self.host, "/$/datasets"),
                                auth=HTTPBasicAuth(self.user,
                                                   self.password))

        if response.status_code != 200:
            raise FusekiException(f"Fuseki server request ({response.url}) returned response {response.status_code}")

        return self._select_repository_names_from_fuseki_response(response_text=response.text)

    @staticmethod
    def _select_repository_names_from_fuseki_response(response_text) -> list:
        """
            Helper method for digging for the list of repository.
        :param response_text:
        :return: list of the repository names
        """
        result = loads(response_text)
        return [d_item['ds.name'][1:] for d_item in result['datasets']]

    def get_sparql_triple_store_endpoint_url(self, repository_name: str) -> str:
        """
            Helper method to create the url for querying.
        :param repository_name:
        :return:
        """
        return urljoin(self.host, f"/{repository_name}/sparql")

    def get_sparql_triple_store_endpoint(self, repository_name: str = None) -> TripleStoreEndpointABC:
        """
            Helper method to create the triple store endpoint for querying.
        :param repository_name: The dataset identifier. This should be short alphanumeric string uniquely
        identifying the repository
        :return: the query url
        """
        endpoint_url = self.get_sparql_triple_store_endpoint_url(repository_name=repository_name)
        sparql_endpoint = SPARQLTripleStoreEndpoint(endpoint_url=endpoint_url, user=self.user, password=self.password)
        return sparql_endpoint

    def _get_repository(self, repository_name: str) -> dict:
        """
        Method to get a repository in order to execute operations on it
        :param repository_name:
        :return:
        """
        response = requests.get(urljoin(self.host, f"/$/datasets/{repository_name}"),
                                auth=HTTPBasicAuth(self.user,
                                                   self.password))

        if response.status_code != 200:
            raise FusekiException(f"Fuseki server request ({response.url}) returned response {response.status_code}")

        return response.json()
