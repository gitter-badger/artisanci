from flask import Blueprint, abort


mod_project = Blueprint('project', __name__, url_prefix='/projects')


@mod_project.route('/', methods=['GET'])
def list_own_projects():
    return abort(501)


@mod_project.route('/<type>/<owner>', methods=['GET'])
def list_user_projects(type, owner):
    return abort(501)


@mod_project.route('/<type>/<owner>/<name>', methods=['GET'])
def show_project(type, owner, name):
    return abort(501)


@mod_project.route('/<type>/<owner>/<name>/<batch>', methods=['GET'])
def show_project_batch(type, owner, name, batch):
    return abort(501)


@mod_project.route('/<type>/<owner>/<name>/<batch>/<build>', methods=['GET'])
def show_project_build(type, owner, name, batch, build):
    return abort(501)
