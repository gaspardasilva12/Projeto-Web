from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/add-pet', methods=['GET', 'POST'])
@login_required
def add_pet():
    from .models import Pet  # Importação local para evitar ciclo
    if request.method == 'POST':
        name = request.form.get('name')
        species = request.form.get('species')
        age = request.form.get('age')

        if not name or not species or not age:
            flash('All fields are required!', category='error')
        else:
            new_pet = Pet(name=name, species=species, age=int(age), user_id=current_user.id)
            db.session.add(new_pet)
            db.session.commit()
            flash('Pet added successfully!', category='success')
            return redirect(url_for('views.home'))

    return render_template("add_pet.html", user=current_user)