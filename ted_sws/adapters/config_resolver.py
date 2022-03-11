#!/usr/bin/python3

# config_resolver.py
# Date:  01/07/2021
# Author: Stratulat Ștefan

"""
    This module aims to provide a simple method of resolving configurations,
    through the process of searching for them in different sources.
"""
import inspect
import logging
import os
from abc import ABC

from ted_sws.adapters.vault_secrets_store import VaultSecretsStore

logger = logging.getLogger(__name__)


class abstractstatic(staticmethod):
    """
        This class serves to create decorators
         with the property of a static method and an abstract method.
    """

    __slots__ = ()

    def __init__(self, function):
        super(abstractstatic, self).__init__(function)
        function.__isabstractmethod__ = True

    __isabstractmethod__ = True


class ConfigResolverABC(ABC):
    """
        This class defines a configuration resolution abstraction.
    """

    @classmethod
    def config_resolve(cls, default_value: str = None) -> str:
        """
            This method aims to search for a configuration and return its value.
        :param default_value: the default return value, if the configuration is not found.
        :return: the value of the search configuration if found, otherwise default_value returns
        """
        config_name = inspect.stack()[1][3]
        return cls._config_resolve(config_name, default_value)

    @abstractstatic
    def _config_resolve(config_name: str, default_value: str = None):
        """
            This abstract method is used to be able to define the configuration search in different environments.
        :param config_name: the name of the configuration you are looking for
        :param default_value: the default return value, if the configuration is not found.
        :return: the value of the search configuration if found, otherwise default_value returns
        """
        raise NotImplementedError


class EnvConfigResolver(ConfigResolverABC):
    """
        This class aims to search for configurations in environment variables.
    """

    def _config_resolve(config_name: str, default_value: str = None):
        value = os.environ.get(config_name, default=default_value)
        logger.debug("[ENV] Value of '" + str(config_name) + "' is " + str(value) + "(supplied default is '" + str(
            default_value) + "')")
        return value


class VaultConfigResolver(ConfigResolverABC):
    """
       This class aims to search for configurations in Vault secrets.
    """

    def _config_resolve(config_name: str, default_value: str = None):
        value = VaultSecretsStore().get_secret(config_name, default_value)
        logger.debug("[VAULT] Value of '" + str(config_name) + "' is " + str(value) + "(supplied default is '" + str(
            default_value) + "')")
        return value


class VaultAndEnvConfigResolver(EnvConfigResolver):
    """
        This class aims to combine the search for configurations in Vault secrets and environmental variables.
    """

    def _config_resolve(config_name: str, default_value: str = None):
        value = VaultSecretsStore().get_secret(config_name, default_value)
        logger.debug(
            "[VAULT&ENV] Value of '" + str(config_name) + "' is " + str(value) + "(supplied default is '" + str(
                default_value) + "')")
        if value is not None:
            os.environ[config_name] = str(value)
            return value
        else:
            value = super()._config_resolve(config_name, default_value)
            logger.debug(
                "[VAULT&ENV] Value of '" + str(config_name) + "' is " + str(value) + "(supplied default is '" + str(
                    default_value) + "')")
            return value
