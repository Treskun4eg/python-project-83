import os
import psycopg2


class Config(object):
    TIMEOUT = int(os.getenv('EXTERNAL_REQUEST_TIMEOUT', 30))
    SECRET_KEY = os.getenv('SECRET_KEY')
    CONNECT = psycopg2.connect(os.getenv('DATABASE_URL'))
