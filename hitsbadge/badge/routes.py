from io import BytesIO

from flask import Blueprint, abort, current_app, send_file, request, redirect

from hitsbadge import db

badge_app = Blueprint('badge_app', __name__)


@badge_app.route('/')
def index():
    return redirect(current_app.config['GITHUB_PAGE'])


@badge_app.route('/<string:key>.svg')
def send_badge(key):
    site_id, err = _get_site(key)
    if err:
        return abort(500)
    if not site_id:
        return abort(404)

    nocount = request.args.get('nocount', default=False, type=lambda x: x == '1')
    counter, err = _add_and_count_hits(site_id, nocount)
    if err:
        return abort(500)

    svg_file = _create_svg(counter)

    return send_file(svg_file, mimetype='image/svg+xml')


@badge_app.after_request
def add_header(r):
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    r.headers['Access-Control-Allow-Origin'] = '*'
    return r


def _get_site(key):
    query = '''
            SELECT
                s.id
            FROM
                sites s
            WHERE
                key=%(key)s;
            '''
    param = {'key': key}
    site_id, err = db.execute(query, param, fetchone=True)
    return site_id, err


def _add_and_count_hits(site_id, nocount):
    if not nocount:
        err = _add_hit(site_id)
        if err:
            return None, err

    initial_hits, err = _get_initial_hits(site_id)
    if err:
        return None, err

    hits, err = _count_hits(site_id)
    if err:
        return None, err

    return initial_hits + hits, None


def _add_hit(site_id):
    query = '''
            INSERT INTO
                hits (id, timestamp, site_id, remote_addr)
            VALUES
                (default, default, %(site_id)s, %(remote_addr)s);
            '''
    param = {'site_id': site_id, 'remote_addr': request.environ['REMOTE_ADDR']}
    _, err = db.execute(query, param)
    return err


def _get_initial_hits(site_id):
    query = '''
            SELECT
                s.initial_hits
            FROM
                sites s
            WHERE
                s.id=%(site_id)s;
            '''
    param = {'site_id': site_id}
    initial_hits, err = db.execute(query, param, fetchone=True)
    return initial_hits[0], err


def _count_hits(site_id):
    query = '''
            SELECT
                COUNT(h.id)
            FROM
                hits h
            WHERE
                h.site_id=%(site_id)s;
            '''
    param = {'site_id': site_id}
    hits, err = db.execute(query, param, fetchone=True)
    return hits[0], err


def _create_svg(counter):
    with open(f'{current_app.root_path}/badge/templates/template.svg') as f:
        svg_text = f.read()

    svg_file = BytesIO()
    svg_file.write(svg_text.format(counter=counter).encode('utf-8'))
    svg_file.seek(0)

    return svg_file
