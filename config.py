import toml

CONFIG = None
try:
    CONFIG = dict(toml.load("config.toml"))
except FileNotFoundError:
    raise Exception("Config file not found")


API_KEY = dict(CONFIG.get("SECRET_KEYS")).get("x_api_key")

ENV = dict(CONFIG.get("ENV")).get("current_env")

DATABASE_URL = dict(CONFIG.get("DATABASE_URL")).get("connection_url")

REDIS_CONECTION_URL = dict(CONFIG.get("REDIS")).get("connection_url")
