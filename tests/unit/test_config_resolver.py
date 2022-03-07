from ted_sws import config


def test_config_resolver():
    mongo_db_url = config.MONGO_DB_AUTH_URL
    assert mongo_db_url
