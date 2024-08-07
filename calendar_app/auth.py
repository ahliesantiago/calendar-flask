import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from calendar_app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/account')
def account():
    return render_template("register.html", pageTitle="Register", pageCss="authStyle")


@bp.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        birthdate = request.form['birthdate']
        email_address = request.form['email']
        password = request.form['password']
        password_confirmation = request.form['confirmPassword']
        db = get_db()
        error = None

        if not first_name:
            error = 'First name is required'
        elif not last_name:
            error = 'Last name is required'
        elif not birthdate:
            error = 'Birthday is required'
        elif not email_address:
            error = 'Email address is required'
        elif not password:
            error = 'Password is required'
        elif password != password_confirmation:
            error = "Passwords don't match"

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (email_address, password, birthdate, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                    (email_address, generate_password_hash(password), birthdate, first_name, last_name)
                )
                db.commit()
            except db.IntegrityError:
                error: f"Email address {email_address} is already registered."
            else:
                return redirect(url_for("auth.login"))
        flash(error)

    return render_template('auth/register.html')
    # return redirect("/")


@bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email_address = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE email_address = ?', (email_address,)
        ).fetchone()

        if user is None:
            error = 'Email address not found'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect email address or password'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for("index"))
        flash(error)

    return render_template('auth/login.html')


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
