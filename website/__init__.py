from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user
from werkzeug.utils import secure_filename
import os

db = SQLAlchemy()
DB_NAME = "database.db"
UPLOAD_FOLDER = 'website/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    db.init_app(app)

    from .models import User, Ong, Pet, Observation

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

    @app.route('/ongs', methods=['GET', 'POST'])
    def listar_ongs():
        if request.method == 'POST':
            nome = request.form['nome']
            descricao = request.form['descricao']
            email = request.form['email']
            telefone = request.form['telefone']
            endereco = request.form['endereco']

            nova_ong = Ong(
                nome=nome,
                descricao=descricao,
                email=email,
                telefone=telefone,
                endereco=endereco
            )
            db.session.add(nova_ong)
            db.session.commit()
            return redirect(url_for('listar_ongs'))

        ongs = Ong.query.all()
        return render_template('ongs.html', ongs=ongs)

    @app.route('/excluir_ong', methods=['POST'])
    def excluir_ong():
        ong_id = request.form['ong_id']
        ong = Ong.query.get(ong_id)
        if ong:
            db.session.delete(ong)
            db.session.commit()
        return redirect(url_for('listar_ongs'))

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/add_pet', methods=['GET', 'POST'])
    def add_pet():
        if request.method == 'POST':
            # ...pegar outros campos...
            if 'image' in request.files:
                file = request.files['image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    image_url = url_for('static', filename=f'uploads/{filename}')
                    # Salve image_url no banco de dados
            # ...restante do código...

    return app

def create_database(app):
    db_path = path.join('website', DB_NAME)
    if not path.exists(db_path):
        with app.app_context():
            db.create_all()
        print('Created Database!')
