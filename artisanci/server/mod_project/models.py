from artisanci.server import db
from artisanci.server.base_model import BaseModel


class Project(BaseModel):
    __tablename__ = 'project'

    type = db.String(length=2, nullable=False)
    url = db.Text(nullable=False)
    name = db.String(length=256, nullable=False)

    owner_id = db.Column(db.Integer, db.ForeignKey('auth.id'))
    owner = db.relationship('Auth', back_populates='projects')

    batches = db.relationship('Batch', back_populates='project')


class Batch(BaseModel):
    __tablename__ = 'batch'

    approved = db.Column(db.Boolean, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', back_populates='batches')

    builds = db.relationship('Build', back_populates='batch')


class Build(BaseModel):
    __tablename__ = 'build'

    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'))
    batch = db.relationship('Batch', back_populates='builds')

    script = db.String(length=256)
    requires = db.Text()
    environment = db.Text()
    output = db.Text()
