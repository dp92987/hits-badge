from io import BytesIO

import requests
from flask import Blueprint, abort, current_app, send_file, request, redirect

from hitsbadge import db

badge_bp = Blueprint('badge_bp', __name__, template_folder='templates')


@badge_bp.route('/')
def index():
    return redirect(current_app.config['GITHUB_PAGE'])


@badge_bp.route('/<string:provider_name>/<string:user_name>/<string:repo_name>.svg')
def svg(provider_name, user_name, repo_name):
    provider, err = _get_provider(provider_name)
    if err:
        return abort(500)
    if not provider:
        return _repo_not_found()

    repo, err = _get_repo(provider['url'], user_name, repo_name)
    if err:
        return abort(500)
    if not repo:
        return _repo_not_found()

    repo_id, err = _create_or_update_repo(provider, repo)
    if err:
        return abort(500)

    nocount = request.args.get('nocount', default=False, type=lambda x: x == '1')
    counter, err = _add_and_count_hits(repo_id, nocount)
    if err:
        return abort(500)

    svg_file = _create_svg(counter)

    return send_file(svg_file, mimetype='image/svg+xml')


@badge_bp.after_request
def add_header(r):
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    r.headers['Access-Control-Allow-Origin'] = '*'
    return r


def _repo_not_found():
    return send_file(_create_svg('not found'), mimetype='image/svg+xml')


def _get_provider(name):
    query = '''
            SELECT
                p.id, p.url, p.field_names
            FROM
                providers p
            WHERE
                p.name = %(name)s;
            '''
    param = {'name': name}
    provider, err = db.execute(query, param, fetchone=True, cursor_factory='DictCursor')
    return provider, err


def _get_repo(provider_url, user_name, repo_name):
    url = provider_url.replace('user_name', user_name).replace('repo_name', repo_name)

    r = requests.get(url)
    if r.status_code == 404:
        return None, None
    if r.status_code != 200:
        return None, (r.status_code, r.reason)

    return r.json(), None


def _get_repo_id(provider_id, internal_id):
    query = '''
            SELECT
                r.id
            FROM
                repos r
            WHERE
                r.provider_id = %(provider_id)s AND r.internal_id = %(internal_id)s;
            '''
    param = {'provider_id': provider_id, 'internal_id': str(internal_id)}
    result, err = db.execute(query, param, fetchone=True)
    if err:
        return None, err

    return result[0] if result else None, None


def _create_or_update_repo(provider, repo):
    repo_id, err = _get_repo_id(provider['id'], repo[provider['field_names']['id']])
    if err:
        return None, err

    owner_id, err = _create_or_update_owner(provider, repo)
    if err:
        return None, err

    if not repo_id:
        repo_id, err = _create_repo(provider, repo, owner_id)
    else:
        err = _update_repo(repo_id, repo, owner_id)
    if err:
        return None, err

    return repo_id, None


def _create_repo(provider, repo, owner_id):
    query = '''
            INSERT INTO
                repos (provider_id, internal_id, name, owner_id)
            VALUES
                (%(provider_id)s, %(internal_id)s, %(name)s, %(owner_id)s)
            RETURNING
                id;
            '''
    param = {
        'provider_id': provider['id'],
        'internal_id': repo[provider['field_names']['id']],
        'name': repo['name'],
        'owner_id': owner_id
    }
    result, err = db.execute(query, param)
    if err:
        return None, err

    return result[0][0] if result else None, None


def _update_repo(repo_id, repo, owner_id):
    query = '''
            UPDATE
                repos r
            SET
                name = %(name)s,
                owner_id = %(owner_id)s
            WHERE
                r.id = %(repo_id)s;
            '''
    param = {'name': repo['name'], 'repo_id': repo_id, 'owner_id': owner_id}
    _, err = db.execute(query, param)
    return err


def _create_or_update_owner(provider, repo):
    owner_field_name = provider['field_names']['owner']
    owner_id_field_name = provider['field_names']['owner_id']

    owner_id, err = _get_owner_id(provider['id'], repo[owner_field_name][owner_id_field_name])
    if err:
        return None, err

    if not owner_id:
        owner_id, err = _create_owner(provider, repo[owner_field_name])
    else:
        err = _update_owner(owner_id, provider, repo[owner_field_name])
    if err:
        return None, err

    return owner_id, None


def _get_owner_id(provider_id, internal_id):
    query = '''
            SELECT
                o.id
            FROM
                owners o
            WHERE
                o.provider_id = %(provider_id)s AND o.internal_id = %(internal_id)s;
            '''
    param = {'provider_id': provider_id, 'internal_id': str(internal_id)}
    result, err = db.execute(query, param, fetchone=True)
    if err:
        return None, err

    return result[0] if result else None, None


def _create_owner(provider, owner):
    query = '''
            INSERT INTO
                owners (provider_id, internal_id, name)
            VALUES
                (%(provider_id)s, %(internal_id)s, %(name)s)
            RETURNING
                id;
            '''
    param = {'provider_id': provider['id'], 'internal_id': owner[provider['field_names']['owner_id']],
             'name': owner[provider['field_names']['owner_name']]}
    result, err = db.execute(query, param)
    if err:
        return None, err

    return result[0][0] if result else None, None


def _update_owner(owner_id, provider, owner):
    query = '''
            UPDATE
                owners o
            SET
                name = %(name)s
            WHERE
                o.id = %(owner_id)s;
            '''
    param = {'name': owner[provider['field_names']['owner_name']], 'owner_id': owner_id}
    _, err = db.execute(query, param)
    return err


def _add_and_count_hits(repo_id, nocount):
    if not nocount:
        err = _add_hit(repo_id)
        if err:
            return None, err

    initial_hits, err = _get_initial_hits(repo_id)
    if err:
        return None, err

    hits, err = _count_hits(repo_id)
    if err:
        return None, err

    return initial_hits + hits, None


def _add_hit(repo_id):
    query = '''
            INSERT INTO
                hits (id, timestamp, repo_id, remote_addr)
            VALUES
                (default, default, %(repo_id)s, %(remote_addr)s);
            '''
    param = {'repo_id': repo_id, 'remote_addr': request.environ['REMOTE_ADDR']}
    _, err = db.execute(query, param)
    return err


def _get_initial_hits(repo_id):
    query = '''
            SELECT
                r.initial_hits
            FROM
                repos r
            WHERE
                r.id = %(repo_id)s;
            '''
    param = {'repo_id': repo_id}
    initial_hits, err = db.execute(query, param, fetchone=True)
    return initial_hits[0], err


def _count_hits(repo_id):
    query = '''
            SELECT
                COUNT(h.id)
            FROM
                hits h
            WHERE
                h.repo_id = %(repo_id)s;
            '''
    param = {'repo_id': repo_id}
    hits, err = db.execute(query, param, fetchone=True)
    return hits[0], err


def _create_svg(counter):
    with open(f'{current_app.root_path}/badge/templates/template.svg') as f:
        svg_text = f.read()

    svg_file = BytesIO()
    svg_file.write(svg_text.format(counter=counter).encode('utf-8'))
    svg_file.seek(0)

    return svg_file
