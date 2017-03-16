import os
from flask import Blueprint, redirect, abort
from artisanci.constants import TYPE_GITHUB, TYPE_GITLAB, TYPE_BITBUCKET
from artisanci.server import db

mod_login = Blueprint('login', __name__, url_prefix='/login')


@mod_login.route('/')
def login_page():
    return ''


@mod_login.route('/oauth/<type>', methods=['GET'])
def oauth_login(type):
    if type == TYPE_GITHUB:
        return abort(501)
    elif type == TYPE_GITLAB:
        return abort(501)
    elif type == TYPE_BITBUCKET:
        return abort(501)
    else:
        return abort(404)


@mod_login.route('/oauth/callbacks/<type>', methods=['POST'])
def oauth_login_callback(type):
    if type == TYPE_GITHUB:
        return abort(501)
    elif type == TYPE_GITLAB:
        return abort(501)
    elif type == TYPE_BITBUCKET:
        return abort(501)
    else:
        return abort(404)