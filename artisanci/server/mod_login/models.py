from artisanci.server import db
from artisanci.server.base_model import BaseModel


class Auth(BaseModel):
    __tablename__ = 'auth'

    type = db.String(length=2, nullable=False)
    name = db.String(length=256, nullable=False)
    access_token = db.String(length=256)
    projects = db.relationship('Project', back_populates='owner')
