SECRET_KEY = 'default'

DATABASE = {
    'host': '127.0.0.1',
    'port': '5432',
    'user': 'pg_user',
    'password': 'pg_password',
    'dbname': 'db_name',
}

DEBUG = True

PROXY_FIX = False
PROXY_FIX_PARAMS = {
    'x_for': 1,
    'x_proto': 1,
    'x_host': 0,
    'x_port': 0,
    'x_prefix': 0,
}
