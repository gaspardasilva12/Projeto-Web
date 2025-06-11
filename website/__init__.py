from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user
from werkzeug.utils import secure_filename
import os
from flask_mail import Mail, Message

db = SQLAlchemy()
mail = Mail()  # moved here for module-level import
DB_NAME = "database.db"
UPLOAD_FOLDER = 'website/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    # Define absolute path of the database
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.instance_path, DB_NAME)}'
    
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    db.init_app(app)

    from .models import User, Ong, Pet, Observation

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @app.context_processor
    def inject_user():
        return dict(user=current_user)

    # Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'gelsonhiluca@gmail.com'
    app.config['MAIL_PASSWORD'] = 'gelson123'
    app.config['MAIL_DEFAULT_SENDER'] = 'gelsonhiluca@gmail.com'
    mail.init_app(app)  # initialize mail with the app

    return app

def create_database(app):
    db_path = os.path.join(app.instance_path, DB_NAME)
    print(db_path)
    if not path.exists(db_path):
        with app.app_context():
            db.create_all()
        print('Created Database!')
