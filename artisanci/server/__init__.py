""" Artisan CI server implementation using Flask, Redis, and a database backend.
Also happens to power `https://artisan.ci` with some additions for documentation. """

try:
    from flask import Flask, session, render_template
    from flask_sqlalchemy import SQLAlchemy
    from flask_redis import FlaskRedis
    import redis
    import jinja2
except ImportError:
    raise ImportError('Could not import all required modules for `artisanci.server`. '
                      'Did you not install using `python -m pip install artisanci[server]`?')

import logging
import os
import sys


def init_app():
    """ Creates the Artisan CI Flask application from environment variables. """
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

    # Setting up server logging
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setFormatter(logging.Formatter('%(asctime)-15s - %(levelname)s - %(message)s'))
    app.logger.addHandler(log_handler)
    app.logger.info('Setting up Artisan CI server instance.')

    # OAuth Applications
    if 'GITHUB_OAUTH_CLIENT_ID' in os.environ and 'GITHUB_OAUTH_CLIENT_SECRET' in os.environ:
        app.logger.info('GitHub OAuth authentication active.')
    else:
        app.logger.warning('GitHub OAuth authentication not active.')
    if 'GITLAB_OAUTH_CLIENT_ID' in os.environ and 'GITLAB_OAUTH_CLIENT_SECRET' in os.environ:
        app.logger.info('GitLab OAuth authentication active.')
    else:
        app.logger.warning('GitLab OAuth authentication not active.')

    if 'SQLALCHEMY_DATABASE_URI' in os.environ:
        app.logger.info('SQLAlchemy using database at `%s`' % os.environ['SQLALCHEMY_DATABASE_URI'])
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
    else:
        app.logger.warning('SQLAlchemy is using a temporary SQLite database.')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

    # Disable `SQLALCHEMY_TRACK_MODIFICATIONS` because it's very slow.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return app


app = init_app()
db = SQLAlchemy(app)
FlaskRedis()

@app.route('/', methods=['GET'])
def index():
    return render_template('parent.html')

from artisanci.server.mod_login.controllers import mod_login as login_module
from artisanci.server.mod_project.controllers import mod_project as project_module

app.register_blueprint(login_module)
app.register_blueprint(project_module)

db.create_all()

