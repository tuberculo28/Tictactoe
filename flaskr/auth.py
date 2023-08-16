import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verifypassword = request.form['verifypassword']
        correo = request.form['correo']
        db = get_db()
        error = None

        if not username:
            error = 'Se necesita un nombre de usuario.'
        elif not password:
            error = 'Se necesita una contraseña.'
        elif not verifypassword:
            error = 'Se necesita una contraseña'
        elif (not verifypassword == password):
            error = 'La contraseña no coincide.'
        elif not correo:
            error = 'Se necesita un email'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, correo, password) VALUES (?, ?, ?)",
                    (username, correo, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"El usuario {username} ya existe."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'El usuario no existe.'
        elif not check_password_hash(user['password'], password):
            error = 'La contraseña es incorrecta.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

