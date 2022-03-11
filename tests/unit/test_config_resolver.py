from ted_sws import config
from ted_sws.adapters.config_resolver import EnvConfigResolver, VaultConfigResolver, VaultAndEnvConfigResolver


def test_config_resolver():
    mongo_db_url = config.MONGO_DB_AUTH_URL
    assert mongo_db_url


def test_env_config_resolver():
    config_value = EnvConfigResolver().config_resolve()
    assert config_value is None


def test_vault_config_resolver():
    config_value = VaultConfigResolver().config_resolve()
    assert config_value is None


def test_vault_and_env_config_resolver():
    config_value = VaultAndEnvConfigResolver().config_resolve()
    assert config_value is None
