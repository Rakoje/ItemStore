from datetime import timedelta
import os

database_url = os.environ["DATABASE_URL"]
redis_host = os.environ["REDIS"]

class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{database_url}/store"
    REDIS_HOST = redis_host
    REDIS_ITEMS_LIST = "items"
    SQLALCHEMY_MAX_OVERFLOW = 10
    SQLALCHEMY_POOL_SIZE = 20
    JWT_SECRET_KEY = "SO_SECRET_EVEN_I_DONT_KNOW_IT"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

