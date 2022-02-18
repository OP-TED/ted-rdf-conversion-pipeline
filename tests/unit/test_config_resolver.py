import os
from ted_sws import config
from mfy_data_core.adapters.vault_secrets_store import VaultSecretsStore



def test_config_resolver():
    print(os.environ.get('VAULT_ADDR'))
    print(os.environ.get('VAULT_TOKEN'))
    print(VaultSecretsStore.default_vault_addr)
    print(VaultSecretsStore.default_vault_token)
    mongo_db_url = config.MONGO_DB_AUTH_URL
    print(mongo_db_url)
    assert mongo_db_url