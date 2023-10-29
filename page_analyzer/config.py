import os
import psycopg2


class Config(object):
    TIMEOUT = int(os.getenv('EXTERNAL_REQUEST_TIMEOUT', 30))
    SECRET_KEY = os.getenv('SECRET_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL')
    CONNECT = psycopg2.connect(DATABASE_URL)
