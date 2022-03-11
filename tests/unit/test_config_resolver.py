from ted_sws import config
from ted_sws.adapters.config_resolver import EnvConfigResolver, VaultConfigResolver


def test_config_resolver():
    mongo_db_url = config.MONGO_DB_AUTH_URL
    assert mongo_db_url


def test_env_config_resolver():
    config_resolver = EnvConfigResolver().config_resolve()
    assert config_resolver is None

def test_vault_config_resolver():
    config_resolver = VaultConfigResolver().config_resolve()
    assert config_resolver is None