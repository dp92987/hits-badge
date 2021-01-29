import os

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from . import db
from .badge.routes import badge_app


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Load the default configuration
    app.config.from_object('config.default')

    # Load the configuration from the instance folder
    app.config.from_pyfile(f'{os.getenv("HITSBADGE_ENV")}.py', silent=True)

    # Load the file specified by the HITSBADGE_CONFIG environment variable
    # Variables defined here will override those in the default configuration
    app.config.from_envvar('HITSBADGE_CONFIG', silent=True)

    if app.config['PROXY_FIX']:
        app.wsgi_app = ProxyFix(app.wsgi_app, **app.config['PROXY_FIX_PARAMS'])

    app.config['GITHUB_PAGE'] = 'https://github.com/dp92987/hits-badge'

    with app.app_context():
        db.init_app(app)
        app.register_blueprint(badge_app)

    return app
