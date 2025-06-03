from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Observation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50))
    address = db.Column(db.String(250))
    date_joined = db.Column(db.DateTime(timezone=True), default=func.now())
    observations = db.relationship('Observation', backref='user', lazy=True)
    pets = db.relationship('Pet', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'


class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    size = db.Column(db.String(50), nullable=False)  
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=False)
    is_adopted = db.Column(db.Boolean, default=False)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Pet {self.name}>'


class Ong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(30), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<ONG {self.nome}>'
from .models import User, Ong, Pet, Observation


