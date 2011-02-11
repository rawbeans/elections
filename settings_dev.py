from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'django.db.backends.mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'test_petitions'             # Or path to database file if using sqlite3.
DATABASE_USER = 'test_master'             # Not used with sqlite3.
DATABASE_PASSWORD = 'hi'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

#MEDIA_ROOT = '/home/sqs/proj/ec/openelections/public'
MEDIA_ROOT = '/Users/trusheim/Desktop/openelections/public'

WEBAUTH_SHARED_SECRET = 'a2d24bf589b1dea3d83f317019e2ff83bf430b8d1c2a3f741dbf7d72f196d8cf6a6d113de356dc77'
WEBAUTH_URL = 'https://www.stanford.edu/~trusheim/cgi-bin/wa-authenticate-test.php'

MEDIA_URL = 'http://localhost/openelections/' #'http://corn24.stanford.edu:32145/'
