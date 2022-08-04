
from flask import Blueprint, Flask, render_template, url_for, request, redirect, flash, session
from models import User, db, Note, Trash
from werkzeug.security import generate_password_hash, check_password_hash
import sys


routes = Blueprint('routes', __name__)


@routes.route('/')
def main():
    return render_template('main.html')
@routes.route('/sign_up', methods=["GET", "POST"])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        users = User.query.filter_by(id=email).first()
        if users:
            flash("Email already exists!", category="error")
        elif len(password) < 6:
            flash("Password must be greater than 5 characters!", category="error")
        else:
            new_user = User(id=email, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            session["user"] = email
            flash("Account created successfully!", category="success")
            return redirect(url_for('routes.home'))
    return render_template('sign_up.html')
@routes.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(id=request.form['email']).first()
        password = request.form['password']
        if user:
            if check_password_hash(user.password, password):
                user = request.form['email']
                session["user"] = user
                return redirect(url_for("routes.home"))
        flash("Incorrect username or password!", category="error")
    return render_template('login.html')

@routes.route('/home', methods=["POST", "GET"])
def home():
    if "user" in session:
        if(request.method == "POST"):
            create_note()
        return render_template('home.html', user_info = User.query.filter_by(id=session["user"]))
    return redirect(url_for('routes.login'))
@routes.route('/notes', methods=['POST', 'GET'])
def notes_link():
    if "user" in session:
        if request.method == 'POST':
            create_note()
        users = session.get("user")
        names = get_note_names()
        if len(names) == 0:
            return render_template('base_notes.html')
        print(names[0], file=sys.stderr)
        return redirect(url_for('routes.notes', name=names[0]))
    return redirect(url_for('routes.login'))
@routes.route('/notes/<name>', methods=["POST", "GET"])
def notes(name):
    if "user" in session:
        users = session.get("user")
        if request.method == 'POST':
            if 'done' in request.form:
                data = request.form['note']
                change_data(data, name)
                return redirect(url_for('routes.notes', name=name))
            elif "new_button" in request.form:
                new_name = create_note()
                return redirect(url_for('routes.notes', name=new_name))
            elif "delete_button" in request.form:
                new_name = delete_note(name)
                return redirect(url_for('routes.notes', name=new_name))
            elif "change" in request.form:
                new_name = change_name(users, name)
                return redirect(url_for('routes.notes', name=new_name))
            elif "log_out_button" in request.form:
                session.pop("user", None)
                return redirect(url_for('routes.login'))
        return render_template('note.html', name=name, values=Note.query.filter_by(id=name), datas=User.query.filter_by(id=users))
    return redirect(url_for('routes.login'))
@routes.route('/account', methods=["GET", "POST"])
def account():
    if "user" in session:
        user = User.query.filter_by(id=session.get("user")).first()
        if request.method == 'POST':
            if "submit" in request.form:
                old_pass = request.form['old_pass']
                if check_password_hash(user.password, old_pass):
                    new_pass = request.form['new_pass']
                    user.password = generate_password_hash(new_pass, method='sha256')
                    db.session.commit()
                    return render_template('account.html', email="password updated")
            elif "log_out_button" in request.form:
                session.pop("user", None)
                return redirect(url_for('routes.login'))
        email = user.id
        return render_template('account.html', email=email)
    return render_template('login.html')
@routes.route('/trash', methods=['GET', 'POST'])
def trash():
    if "user" in session:
        user = User.query.filter_by(id=session.get("user")).first()
        return render_template('trash.html', user=User.query.filter_by(id=session.get("user")))
    return redirect(url_for('routes.login'))

def change_name(users, name):
            new_name = request.form['title']
            user = User.query.filter_by(id=users)
            if new_name in get_note_names():
                flash("Name already exists!", category="error")
                return 0
            for notes in user:
                for note in notes.notes:
                    if name == note.id:
                        note.id = new_name
                        db.session.commit()
                        return new_name

def get_note_names():
    user = User.query.filter_by(id=session.get("user"))
    note_names=[]
    for notes in user:
        for note in notes.notes:
            note_names.append(note.id)
    return note_names
def create_note():
    users = session["user"]
    note_names_in_db = get_note_names()
    name = 'untitled'
    i = 1
    while name in note_names_in_db:
        name = name[0:8] 
        name += str(i)
        i += 1
    new_note = Note(id=name, user_id=users, data="Remove this message before typing")
    db.session.add(new_note)
    db.session.commit()
    flash("note added", category='success')
    return name
def delete_note(name_delete):
    note_names_in_db = get_note_names()
    for name in note_names_in_db:
        if name == name_delete:
            trash_note = Trash(name=name, user_id=session.get("user"), data=Note.query.filter_by(id=name).first().data)
            db.session.add(trash_note)
            db.session.commit()
            db.session.delete(Note.query.filter_by(id=name).first())
            db.session.commit()
            note_names_in_db.remove(name)
            return (note_names_in_db[0])
def change_data(data, name):
    #name = request.form['title']
    print(data, file=sys.stderr)
    user = User.query.filter_by(id=session.get("user"))
    for notes in user:
        for note in notes.notes:
            if note.id == name:
                note.data = data#.strip()
                db.session.commit()

                       