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
from abc import ABC, abstractmethod
from typing import Type

from ted_sws.core.adapters.vault_secrets_store import VaultSecretsStore

logger = logging.getLogger(__name__)


class ConfigResolverABC(ABC):
    """
        This class defines a configuration resolution abstraction.
    """

    def config_resolve(self, default_value: str = None) -> str:
        """
            This method aims to search for a configuration and return its value.
        :param default_value: the default return value, if the configuration is not found.
        :return: the value of the search configuration if found, otherwise default_value returns
        """
        config_name = inspect.stack()[1][3]
        return self.concrete_config_resolve(config_name, default_value)

    @abstractmethod
    def concrete_config_resolve(self, config_name: str, default_value: str = None):
        """
            This abstract method is used to be able to define the configuration search in different environments.
        :param config_name: the name of the configuration you are looking for
        :param default_value: the default return value, if the configuration is not found.
        :return: the value of the search configuration if found, otherwise default_value returns
        """
        raise NotImplementedError


class AirflowConfigResolver(ConfigResolverABC):
    """
        This class aims to search for configurations in Airflow environment variables.
    """

    def concrete_config_resolve(self, config_name: str, default_value: str = None):
        """
            This method retrieve configuration values from Airflow environment.
        :param config_name:
        :param default_value:
        :return:
        """
        try:
            from airflow.models import Variable
            value = Variable.get(key=config_name, default_var=default_value)
            logger.debug(
                "[Airflow ENV] Value of '" + str(config_name) + "' is " + str(value) + "(supplied default is '" + str(
                    default_value) + "')")
            return value
        except:
            return None


class EnvConfigResolver(ConfigResolverABC):
    """
        This class aims to search for configurations in environment variables.
    """

    def concrete_config_resolve(self, config_name: str, default_value: str = None):
        value = os.environ.get(config_name, default=default_value)
        logger.debug("[ENV] Value of '" + str(config_name) + "' is " + str(value) + "(supplied default is '" + str(
            default_value) + "')")
        return value


class AirflowAndEnvConfigResolver(ConfigResolverABC):
    """
            This class aims to combine the search for configurations in Airflow secrets and environmental variables.
    """

    def concrete_config_resolve(self, config_name: str, default_value: str = None):
        value = AirflowConfigResolver().concrete_config_resolve(config_name=config_name)
        if value is not None:
            return value
        else:
            return EnvConfigResolver().concrete_config_resolve(config_name, default_value)


class VaultConfigResolver(ConfigResolverABC):
    """
       This class aims to search for configurations in Vault secrets.
    """

    def concrete_config_resolve(self, config_name: str, default_value: str = None):
        value = VaultSecretsStore().get_secret(config_name, default_value)
        logger.debug("[VAULT] Value of '" + str(config_name) + "' is " + str(value) + "(supplied default is '" + str(
            default_value) + "')")
        return value


class VaultAndEnvConfigResolver(ConfigResolverABC):
    """
        This class aims to combine the search for configurations in Vault secrets and environmental variables.
    """

    def concrete_config_resolve(self, config_name: str, default_value: str = None):
        value = VaultConfigResolver().concrete_config_resolve(config_name)
        if value is not None:
            os.environ[config_name] = str(value)
            return value
        else:
            value = EnvConfigResolver().concrete_config_resolve(config_name, default_value)
            return value


def env_property(config_resolver_class: Type[ConfigResolverABC] = EnvConfigResolver,
                 default_value: str = None):
    """
        This function provide decorator mechanism for config resolver.
    :param config_resolver_class:
    :param default_value:
    :return:
    """
    def wrap(func):
        @property
        def wrapped_function(self, *args, **kwargs):
            config_value = config_resolver_class().concrete_config_resolve(config_name=func.__name__,
                                                                           default_value=default_value)
            return func(self, config_value, *args, **kwargs)

        return wrapped_function

    return wrap