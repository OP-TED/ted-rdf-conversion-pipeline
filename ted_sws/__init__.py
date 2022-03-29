#!/usr/bin/python3

# __init__.py
# Date:  03/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

""" """

__version__ = "0.0.1"

import os

import dotenv
from ted_sws.core.adapters.config_resolver import VaultAndEnvConfigResolver
from ted_sws.core.adapters.vault_secrets_store import VaultSecretsStore

dotenv.load_dotenv(verbose=True, override=True)

SECRET_PATHS = ['mongo-db']
SECRET_MOUNT = f'ted-{os.environ.get("ENVIRONMENT", default="staging")}'

VaultSecretsStore.default_secret_mount = SECRET_MOUNT
VaultSecretsStore.default_secret_paths = SECRET_PATHS


class MongoDBConfig:

    @property
    def MONGO_DB_AUTH_URL(self) -> str:
        if self.ENVIRONMENT == "dev" and self.AIRFLOW__CORE__EXECUTOR:
            return self.MONGO_DB_AUTH_URL_DEV_CONTAINER
        return VaultAndEnvConfigResolver().config_resolve()

    @property
    def MONGO_DB_AUTH_URL_DEV_CONTAINER(self) -> str:
        """
        This variable is to be used only on dev environment when execution is done from a docker container as oppose to
        development host environment
        """
        return VaultAndEnvConfigResolver().config_resolve()

    @property
    def ENVIRONMENT(self) -> str:
        return VaultAndEnvConfigResolver().config_resolve()

    @property
    def AIRFLOW__CORE__EXECUTOR(self) -> str:
        return VaultAndEnvConfigResolver().config_resolve()

    @property
    def MONGO_DB_PORT(self) -> int:
        return int(VaultAndEnvConfigResolver().config_resolve())


    @property
    def MONGO_DB_AGGREGATES_DATABASE_NAME(self) -> str:
        return VaultAndEnvConfigResolver().config_resolve()



class RMLMapperConfig:

    @property
    def RML_MAPPER_PATH(self) -> str:
        return VaultAndEnvConfigResolver().config_resolve()


class TedConfigResolver(MongoDBConfig, RMLMapperConfig):
    """
        This class resolve the secrets of the ted-sws project.
    """


config = TedConfigResolver()

