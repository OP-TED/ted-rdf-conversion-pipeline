from franz.openrdf.repository import Repository
from franz.openrdf.sail import AllegroGraphServer


class AllegroGraphTripleStore:
    """
        This class is handling interactions with Allegro Graph triple store
        Note: If catalog name is not set, every operation will be executed at root level in the triple store
    """
    def __init__(self, host: str, user: str, password: str, catalog_name=None):
        self.host = host
        self.user = user
        self.password = password
        self.catalog_name = catalog_name
        self.allegro = AllegroGraphServer(host=self.host, port=443,
                                          user=self.user, password=self.password, verifypeer=0)

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
        return self.allegro.openCatalog().getRepository(name=repository_name, access_verb=Repository.ACCESS)

    def list_repositories(self):
        """
        Method to list all repositories
        :return:
        """
        return self.allegro.openCatalog(name=self.catalog_name).listRepositories()

    def add_data_to_repository(self, file_content: str, repository_name: str):
        """
        Method to add triples from a string
        :param file_content:
        :param repository_name:
        :return:
        """
        repository = self._get_repository(repository_name=repository_name)
        repository.getConnection().addData(data=file_content)

    def add_file_to_repository(self, file_path, repository_name):
        """
        Method to add triples from a file
        :param file_path:
        :param repository_name:
        :return:
        """
        repository = self._get_repository(repository_name=repository_name)
        repository.getConnection().addFile(filePath=file_path)
