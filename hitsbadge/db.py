from flask import current_app, g
import psycopg2
import psycopg2.extras
import psycopg2.pool


def init_app(app):
    app.config['POOL'] = psycopg2.pool.SimpleConnectionPool(1, 20, **app.config['DATABASE'])
    app.teardown_appcontext(_put_conn)


def execute(sql, vars_=None, batch=False, cursor_factory=None, fetchone=False):
    factories = {'DictCursor': psycopg2.extras.DictCursor,
                 'RealDictCursor': psycopg2.extras.RealDictCursor}
    conn = _get_conn()
    curs = conn.cursor(cursor_factory=factories.get(cursor_factory))
    try:
        if batch:
            psycopg2.extras.execute_batch(curs, sql, vars_)
        else:
            curs.execute(sql, vars_)
        result = curs.fetchone() if fetchone else curs.fetchall() if curs.description else None
    except psycopg2.Error as err:
        conn.rollback()
        return None, err
    else:
        conn.commit()
        return result, None
    finally:
        curs.close()


def _get_conn():
    if 'conn' not in g:
        g.conn = current_app.config['POOL'].getconn()

    if not _is_conn_alive():
        del g.conn
        g.conn = _get_conn()

    return g.conn


def _put_conn(exc):
    conn = g.pop('conn', None)
    if conn is not None:
        current_app.config['POOL'].putconn(conn)


def _is_conn_alive():
    curs = g.conn.cursor()
    try:
        curs.execute('SELECT 1;')
        return True
    except psycopg2.OperationalError:
        return False
    finally:
        curs.close()
