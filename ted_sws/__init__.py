#!/usr/bin/python3

# __init__.py
# Date:  03/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

""" """

__version__ = "0.0.1"

import os

import dotenv

from ted_sws.core.adapters.config_resolver import EnvConfigResolver

dotenv.load_dotenv(verbose=True, override=os.environ.get('IS_PRIME_ENV') != 'true')

# The RUN_ENV constants define the module execution context of the code.
# By using them, the behaviour of global services, such as logging,
# that cannot be injected in every function signature, can be customized on module level.
RUN_ENV_NAME = "__TED_SWS_RUN_ENV__"
RUN_ENV_VAL = "ted-sws"
RUN_TEST_ENV_VAL = "test"
os.environ[RUN_ENV_NAME] = RUN_ENV_VAL


# SECRET_PATHS = ['mongo-db', 'github']
# SECRET_MOUNT = f'ted-{ENV}'
# VaultSecretsStore.default_secret_mount = SECRET_MOUNT
# VaultSecretsStore.default_secret_paths = SECRET_PATHS


class MongoDBConfig:

    @property
    def MONGO_DB_AUTH_URL(self) -> str:
        if self.ENVIRONMENT == "dev" and self.AIRFLOW__CORE__EXECUTOR:
            return self.MONGO_DB_AUTH_URL_DEV_CONTAINER
        return EnvConfigResolver().config_resolve()

    @property
    def MONGO_DB_AUTH_URL_DEV_CONTAINER(self) -> str:
        """
        This variable is to be used only on dev environment when execution is done from a docker container as oppose to
        development host environment
        """
        return EnvConfigResolver().config_resolve()

    @property
    def ENVIRONMENT(self) -> str:
        return EnvConfigResolver().config_resolve()

    @property
    def AIRFLOW__CORE__EXECUTOR(self) -> str:
        return EnvConfigResolver().config_resolve()

    @property
    def MONGO_DB_PORT(self) -> int:
        return int(EnvConfigResolver().config_resolve())

    @property
    def MONGO_DB_AGGREGATES_DATABASE_NAME(self) -> str:
        return EnvConfigResolver().config_resolve()


class RMLMapperConfig:
    @property
    def RML_MAPPER_PATH(self) -> str:
        return EnvConfigResolver().config_resolve()


class AllegroConfig:
    @property
    def AGRAPH_SUPER_USER(self) -> str:
        return EnvConfigResolver().config_resolve()

    @property
    def AGRAPH_SUPER_PASSWORD(self) -> str:
        return EnvConfigResolver().config_resolve()

    @property
    def ALLEGRO_HOST(self) -> str:
        return EnvConfigResolver().config_resolve()


class ELKConfig:

    @property
    def ELK_HOST(self) -> str:
        return EnvConfigResolver().config_resolve()

    @property
    def ELK_PORT(self) -> int:
        v: str = EnvConfigResolver().config_resolve()
        return int(v) if v is not None else None

    @property
    def ELK_VERSION(self) -> int:
        v: str = EnvConfigResolver().config_resolve()
        return int(v) if v is not None else None


class LoggingConfig:
    @property
    def MONGO_DB_LOGS_DATABASE_NAME(self) -> str:
        return EnvConfigResolver().config_resolve()

    @property
    def DAG_LOGGER_CONFIG_HANDLERS(self) -> str:
        return EnvConfigResolver().config_resolve()

    @property
    def CLI_LOGGER_CONFIG_HANDLERS(self) -> str:
        return EnvConfigResolver().config_resolve()

    @property
    def LOGGER_LOG_FILENAME(self) -> str:
        return EnvConfigResolver().config_resolve()


class XMLProcessorConfig:

    @property
    def XML_PROCESSOR_PATH(self) -> str:
        return EnvConfigResolver().config_resolve()


class GitHubArtefacts:

    @property
    def GITHUB_TED_SWS_ARTEFACTS_URL(self) -> str:
        return EnvConfigResolver().config_resolve()


class API:
    @property
    def ID_MANAGER_API_HOST(self) -> str:
        v: str = EnvConfigResolver().config_resolve()
        return v if v else "localhost"

    @property
    def ID_MANAGER_API_PORT(self) -> int:
        v: str = EnvConfigResolver().config_resolve()
        return int(v) if v else 8000


class TedAPIConfig:
    @property
    def TED_API_URL(self) -> str:
        return EnvConfigResolver().config_resolve()


class TedConfigResolver(MongoDBConfig, RMLMapperConfig, XMLProcessorConfig, ELKConfig, LoggingConfig,
                        GitHubArtefacts, API, AllegroConfig, TedAPIConfig):
    """
        This class resolve the secrets of the ted-sws project.
    """


config = TedConfigResolver()
