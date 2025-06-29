from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import logout_user, login_required, current_user
from .models import Observation, Pet, Ong
from . import db, mail
import json
from werkzeug.utils import secure_filename
import os
from  flask_mail import Message

views = Blueprint('views', __name__)
UPLOAD_FOLDER = 'website/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@views.route('/', methods=['GET'])
@login_required
def home():
    return render_template("home.html", user=current_user)

#CRUD Observações
@views.route('/observations', methods=['GET', 'POST'])
@login_required
def observations():
    if request.method == 'POST':
        observation_text = request.form.get('observation')
        if observation_text and len(observation_text.strip()) > 0:
            new_observation = Observation(data=observation_text, user_id=current_user.id)
            db.session.add(new_observation)
            db.session.commit()
            flash('Observation added!', category='success')
        else:
            flash('Observation is too short!', category='error')
        return redirect(url_for('views.observations'))

    user_observations = Observation.query.filter_by(user_id=current_user.id).all()
    return render_template("observations.html", user=current_user, observations=user_observations)

@views.route('/delete-observation', methods=['POST'])
@login_required
def delete_observation():
    data = json.loads(request.data)
    observation_id = data.get('observationId')
    observation = Observation.query.get(observation_id)
    if observation and observation.user_id == current_user.id:
        db.session.delete(observation)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

###########################################################################################################
#CRUD Pets

@views.route('/add_pet', methods=['GET', 'POST'])
@login_required
def add_pet():
    if request.method == 'POST':
        name = request.form.get('name')
        species = request.form.get('species')
        age = int(request.form.get('age'))
        size = request.form.get('size')
        description = request.form.get('description')

        # Verifica se uma imagem foi enviada
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            image_filename = secure_filename(image_file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, image_filename)
            image_file.save(filepath)
        else:
            # Atribui uma imagem padrão caso nenhuma imagem seja enviada
            image_filename = 'default_pet.jpg'
        
        pet = Pet(
            name=name,
            species=species,
            age=age,
            size=size,
            description=description,
            image=image_filename,
            is_adopted=False,
            user_id=current_user.id
        )
        
        db.session.add(pet)
        db.session.commit()
        flash('Pet added successfully!', category='success')
        return redirect(url_for('views.my_pets'))

    return render_template("add_pet.html", user=current_user)

@views.route("/pets", methods=['GET'])
@login_required
def get_all_pets():
    name_query = request.args.get('name', '')

    if name_query:
        pets = Pet.query.filter(Pet.name.ilike(f"%{name_query}%")).all()
    else:
        pets = Pet.query.all()

    return render_template("my_pets.html", user=current_user, pets=pets)    

@views.route('/my-pets', methods=['GET'])
@login_required
def my_pets():
    pets = current_user.pets
    return render_template("my_pets.html", user=current_user, pets=pets)

@views.route('/pets/<int:pet_id>', methods=['GET'])
@login_required
def view_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return render_template('pet_detail.html', user=current_user, pet=pet)

@views.route('/pets/<int:pet_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.user_id != current_user.id:
        flash('You do not have permission to edit this pet.', 'error')
        return redirect(url_for('views.get_all_pets'))
    if request.method == 'POST':
        pet.name = request.form.get('name')
        pet.species = request.form.get('species')
        pet.age = request.form.get('age')
        pet.size = request.form.get('size')
        pet.description = request.form.get('description')
        pet.image = request.form.get('image')
        db.session.commit()
        flash('Pet updated successfully!', 'success')
        return redirect(url_for('views.get_profile'))
    return render_template('edit_pet.html', user=current_user, pet=pet)

@views.route('/delete-pet/<int:pet_id>', methods=['POST'])
@login_required
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.user_id != current_user.id:
        flash('You do not have permission to delete this pet.', 'error')
        return redirect(url_for('views.get_all_pets'))
    db.session.delete(pet)
    db.session.commit()
    flash('Pet deleted successfully!', 'success')
    return redirect(url_for('views.get_profile'))

###########################################################################################################
#CRUD Perfil

@views.route('/profile', methods=['GET', 'POST'])
@login_required
def get_profile():
    pets = current_user.pets
    user = current_user._get_current_object()
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')
        current_user.address = request.form.get('address')
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('views.get_profile'))
    return render_template("profile.html", user=user, pets=pets)  

@views.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user = current_user._get_current_object()  
    db.session.delete(user)
    db.session.commit()
    logout_user()
    flash('Account deleted successfully!', category='success')
    return redirect(url_for('auth.login'))

@views.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')
        current_user.address = request.form.get('address')
        db.session.commit()
        flash('Profile updated successfully!', category='success')
        return redirect(url_for('views.get_profile'))
    return render_template('edit_profile.html', user=current_user)

@views.route("/about")
def about():
    return render_template("about.html")

@views.route('/adoption')
def adoption():
    pets = Pet.query.all()
    return render_template('adoption.html', pets=pets)

@views.route('/adopt-pet/<int:pet_id>', methods=['POST'])
@login_required
def adopt_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if pet and not pet.is_adopted:
        pet.is_adopted = True
        db.session.commit()
        flash(f'You have successfully adopted {pet.name}!', category='success')
    else:
        flash('This pet has already been adopted.', category='error')
    return redirect(url_for('views.adoption'))

###########################################################################################################
#CRUD ONG

@views.route('/add-ong', methods=['GET', 'POST'])
@login_required
def criar_ongs():
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
        print(nova_ong)
        db.session.commit()
        return redirect(url_for('views.listar_ongs'))

    ongs = Ong.query.all()
    return render_template('add_ongs.html', ongs=ongs)

@views.route('/ongs/<int:ong_id>', methods=['GET'])
@login_required
def view_ong(ong_id):
    ong = Ong.query.get_or_404(ong_id)
    return render_template('ong_detail.html', user=current_user, ong=ong)

@views.route("/ongs", methods=['GET'])
@login_required
def listar_ongs():
    name_query = request.args.get('nome', '')

    if name_query:
        ongs = Ong.query.filter(Ong.nome.ilike(f"%{name_query}%")).all()
    else:
        ongs = Ong.query.all()

    return render_template("ongs.html", user=current_user, ongs=ongs) 

@views.route('/ongs/<int:ong_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_ong(ong_id):
    ong = Ong.query.get_or_404(ong_id)
    if ong.user_id != current_user.id:
        flash('You do not have permission to edit this pet.', 'error')
        return redirect(url_for('views.get_all_pets'))
    if request.method == 'POST':
        ong.nome = request.form.get('nome')
        ong.descricao = request.form.get('descricao')
        ong.email = request.form.get('email')
        ong.telefone = request.form.get('telefone')
        ong.endereco = request.form.get('endereco')
        db.session.commit()
        flash('ONG updated successfully!', 'success')
        return redirect(url_for('views.get_profile'))
    return render_template('ongs.html', user=current_user, ong=ong)

@views.route('/excluir_ong/<int:ong_id>', methods=['POST'])
@login_required
def excluir_ong(ong_id):
    # ong_id = request.form['ong_id']
    ong = Ong.query.get(ong_id)
    if ong:
        db.session.delete(ong)
        db.session.commit()
    return redirect(url_for('views.listar_ongs'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@views.route('/send-email', methods=['POST'])
@login_required
def send_email():
    msg = Message('password recovery', recipients=[request.form['email']])
    msg.body = f"Choose your new password, by clicking on the link: {url_for('views.recover_password', _external=True)}"
    mail.send(msg)
    flash('Recovery email sent!', category='success')
    return redirect(url_for('views.home'))

@views.route('/recover_password', methods=['GET', 'POST'])
def recover_password():
    if request.method == 'POST':
        # Aqui deve ser implementada a lógica de redefinição da senha.
        flash('Your password has been reset. Please login with your new password.', category='success')
        return redirect(url_for('auth.login'))
    return render_template('recover_password.html')


