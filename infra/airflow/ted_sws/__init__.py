#!/usr/bin/python3

# __init__.py
# Date:  03/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

""" """

__version__ = "0.0.1"

import json
import os
import pathlib
import base64
import dotenv

from ted_sws.core.adapters.config_resolver import EnvConfigResolver, AirflowAndEnvConfigResolver, env_property

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

PROJECT_PATH = pathlib.Path(__file__).parent.resolve()
SPARQL_PREFIXES_PATH = PROJECT_PATH / "resources" / "prefixes" / "prefixes.json"


class MongoDBConfig:

    @env_property()
    def MONGO_DB_AUTH_URL(self, config_value: str) -> str:
        if self.ENVIRONMENT == "dev" and self.AIRFLOW__CORE__EXECUTOR:
            return self.MONGO_DB_AUTH_URL_DEV_CONTAINER
        return config_value

    @env_property()
    def MONGO_DB_AUTH_URL_DEV_CONTAINER(self, config_value: str) -> str:
        """
        This variable is to be used only on dev environment when execution is done from a docker container as oppose to
        development host environment
        """
        return config_value

    @env_property()
    def ENVIRONMENT(self, config_value: str) -> str:
        return config_value

    @env_property()
    def AIRFLOW__CORE__EXECUTOR(self, config_value: str) -> str:
        return config_value

    @env_property()
    def MONGO_DB_PORT(self, config_value: str) -> int:
        return int(config_value)

    @env_property(default_value="aggregates_db")
    def MONGO_DB_AGGREGATES_DATABASE_NAME(self, config_value: str) -> str:
        return config_value


class RMLMapperConfig:
    @env_property()
    def RML_MAPPER_PATH(self, config_value: str) -> str:
        return config_value


class LimesAlignmentConfig:
    @env_property()
    def LIMES_ALIGNMENT_PATH(self, config_value: str) -> str:
        return config_value


class AllegroConfig:
    @env_property()
    def AGRAPH_SUPER_USER(self, config_value: str) -> str:
        return config_value

    @env_property()
    def AGRAPH_SUPER_PASSWORD(self, config_value: str) -> str:
        return config_value

    @env_property()
    def ALLEGRO_HOST(self, config_value: str) -> str:
        return config_value

    @env_property()
    def TRIPLE_STORE_ENDPOINT_URL(self, config_value: str) -> str:
        return config_value


class ELKConfig:

    @env_property()
    def ELK_HOST(self, config_value: str) -> str:
        return config_value

    @env_property()
    def ELK_PORT(self, config_value: str) -> int:
        return int(config_value) if config_value is not None else None

    @env_property()
    def ELK_VERSION(self, config_value: str) -> int:
        return int(config_value) if config_value is not None else None


class LoggingConfig:
    @env_property(default_value="aggregates_db")
    def MONGO_DB_LOGS_DATABASE_NAME(self, config_value: str) -> str:
        return config_value

    @env_property()
    def DAG_LOGGER_CONFIG_HANDLERS(self, config_value: str) -> str:
        return config_value

    @env_property()
    def CLI_LOGGER_CONFIG_HANDLERS(self, config_value: str) -> str:
        return config_value

    @env_property()
    def LOGGER_LOG_FILENAME(self, config_value: str) -> str:
        return config_value


class XMLProcessorConfig:

    @env_property()
    def XML_PROCESSOR_PATH(self, config_value: str) -> str:
        return config_value


class GitHubArtefacts:

    @env_property()
    def GITHUB_TED_SWS_ARTEFACTS_URL(self, config_value: str) -> str:
        return config_value



class API:
    @env_property(default_value="localhost")
    def ID_MANAGER_PROD_API_HOST(self, config_value: str) -> str:
        return config_value

    @env_property(default_value="localhost")
    def ID_MANAGER_DEV_API_HOST(self, config_value: str) -> str:
        return config_value

    @env_property(default_value="8000")
    def ID_MANAGER_API_PORT(self, config_value: str) -> int:
        return int(config_value)


class TedAPIConfig:
    @env_property()
    def TED_API_URL(self, config_value: str) -> str:
        return config_value


class FusekiConfig:
    @env_property()
    def FUSEKI_ADMIN_USER(self, config_value: str) -> str:
        return config_value

    @env_property()
    def FUSEKI_ADMIN_PASSWORD(self, config_value: str) -> str:
        return config_value

    @env_property()
    def FUSEKI_ADMIN_HOST(self, config_value: str) -> str:
        return config_value


class SFTPConfig:
    @env_property(config_resolver_class=AirflowAndEnvConfigResolver)
    def SFTP_PUBLISH_HOST(self, config_value: str) -> str:
        return config_value

    @env_property(config_resolver_class=AirflowAndEnvConfigResolver, default_value="22")
    def SFTP_PUBLISH_PORT(self, config_value: str) -> int:
        return int(config_value)

    @env_property(config_resolver_class=AirflowAndEnvConfigResolver)
    def SFTP_PUBLISH_USER(self, config_value: str) -> str:
        return config_value

    @env_property(config_resolver_class=AirflowAndEnvConfigResolver)
    def SFTP_PUBLISH_PASSWORD(self, config_value: str) -> str:
        return config_value

    @env_property(config_resolver_class=AirflowAndEnvConfigResolver)
    def SFTP_PUBLISH_PATH(self, config_value: str) -> str:
        return config_value

    @env_property(config_resolver_class=AirflowAndEnvConfigResolver)
    def SFTP_PRIVATE_KEY_BASE64(self, config_value: str) -> str:
        return config_value

    @env_property(config_resolver_class=AirflowAndEnvConfigResolver)
    def SFTP_PRIVATE_KEY_PASSPHRASE(self, config_value: str) -> str:
        return config_value

    @property
    def SFTP_PRIVATE_KEY(self) -> str:
        sftp_private_key_base64 = self.SFTP_PRIVATE_KEY_BASE64
        if sftp_private_key_base64:
            sftp_private_key_base64 = base64.b64decode(str(sftp_private_key_base64)).decode(encoding="utf-8")
        return sftp_private_key_base64


class SPARQLConfig:

    @property
    def SPARQL_PREFIXES(self) -> dict:
        return json.loads(SPARQL_PREFIXES_PATH.read_text(encoding="utf-8"))["prefix_definitions"]


class S3PublishConfig:
    @env_property(config_resolver_class=AirflowAndEnvConfigResolver)
    def S3_PUBLISH_USER(self, config_value: str) -> str:
        return config_value

    @env_property(config_resolver_class=AirflowAndEnvConfigResolver)
    def S3_PUBLISH_PASSWORD(self, config_value: str) -> str:
        return config_value

    @env_property(config_resolver_class=AirflowAndEnvConfigResolver)
    def S3_PUBLISH_HOST(self, config_value: str) -> str:
        return config_value

    @env_property(config_resolver_class=AirflowAndEnvConfigResolver, default_value="false")
    def S3_PUBLISH_SECURE(self, config_value: str) -> bool:
        return config_value.lower() in ["1", "true"]

    @env_property(config_resolver_class=AirflowAndEnvConfigResolver)
    def S3_PUBLISH_REGION(self, config_value: str) -> str:
        return config_value

    @env_property(config_resolver_class=AirflowAndEnvConfigResolver, default_value="false")
    def S3_PUBLISH_SSL_VERIFY(self, config_value: str) -> bool:
        return config_value.lower() in ["1", "true"]

    @env_property(config_resolver_class=AirflowAndEnvConfigResolver, default_value="notice")
    def S3_PUBLISH_NOTICE_BUCKET(self, config_value: str) -> str:
        return config_value

    @env_property(config_resolver_class=AirflowAndEnvConfigResolver, default_value="notice-rdf")
    def S3_PUBLISH_NOTICE_RDF_BUCKET(self, config_value: str) -> str:
        return config_value

    @env_property(config_resolver_class=AirflowAndEnvConfigResolver, default_value="false")
    def S3_PUBLISH_ENABLED(self, config_value: str) -> bool:
        return config_value.lower() in ["1", "true"]


class TedConfigResolver(MongoDBConfig, RMLMapperConfig, XMLProcessorConfig, ELKConfig, LoggingConfig,
                        GitHubArtefacts, API, AllegroConfig, TedAPIConfig, SFTPConfig, FusekiConfig,
                        SPARQLConfig, LimesAlignmentConfig, S3PublishConfig):
    """
        This class resolve the secrets of the ted-sws project.
    """


config = TedConfigResolver()
