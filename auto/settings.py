import os.path

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SYNC_TIMEOUT = 10
DATABASE = {
    'host': 'localhost',
    'port': 5432,
    'database': 'auto_collector',
    'user': 'postgres',
    'password': 'p0stgres',
}
SITE_ADDR = '0.0.0.0'
SITE_PORT = 8080

TEMPLATE_DIR = os.path.join(BASE_DIR, 'auto', 'templates')
STATIC_URL = '/static'
STATIC_ROOT = os.path.join(BASE_DIR, 'frontend', 'static')
