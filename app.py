import os
import re
import secrets
import sqlite3
from functools import wraps

from flask import (
    Flask, abort, flash, redirect, render_template, request, session, url_for,
)

from auth import (
    add_to_db, check_pass, count_passwords, delete_password, get_passwords,
    get_user, get_user_salt, hashing_a_pass, save_password,
    update_password_value,
)
from crypto import InvalidToken, decrypt_secret, derive_key, encrypt_secret, is_encrypted
from database import init_db

USERNAME_RE = re.compile(r'^[A-Za-z0-9._-]{3,32}$')
MIN_PASSWORD_LENGTH = 8


def load_secret_key():
    """Use SECRET_KEY from the environment, or a key persisted next to the app.

    A hardcoded key would let anyone who reads the source forge session
    cookies; a random key per start would log everyone out on restart.
    """
    env_key = os.environ.get('SECRET_KEY')
    if env_key:
        return env_key
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.secret_key')
    if os.path.exists(key_path):
        with open(key_path) as f:
            return f.read().strip()
    key = secrets.token_hex(32)
    with open(key_path, 'w') as f:
        f.write(key)
    return key


app = Flask(__name__)
app.secret_key = load_secret_key()
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)
init_db()


# --- CSRF protection -------------------------------------------------------

def csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(16)
    return session['_csrf_token']


app.jinja_env.globals['csrf_token'] = csrf_token


@app.before_request
def csrf_protect():
    if request.method == 'POST':
        token = session.get('_csrf_token')
        if not token or token != request.form.get('_csrf_token'):
            abort(400)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'username' not in session:
            flash('Sign in to continue.', 'error')
            return redirect(url_for('login_page'))
        return view(*args, **kwargs)
    return wrapped


# --- Public pages ----------------------------------------------------------

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET'])
def login_page():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    stored_hash = get_user(username)
    if stored_hash and check_pass(password, stored_hash):
        session.clear()
        session['username'] = username
        return redirect(url_for('dashboard'))
    flash('Incorrect username or password.', 'error')
    return render_template('login.html', username=username), 401


@app.route('/register', methods=['GET'])
def register_page():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not USERNAME_RE.match(username):
        flash('Usernames are 3–32 characters: letters, numbers, dots, dashes, underscores.', 'error')
        return render_template('register.html', username=username), 400
    if len(password) < MIN_PASSWORD_LENGTH:
        flash(f'Master password must be at least {MIN_PASSWORD_LENGTH} characters.', 'error')
        return render_template('register.html', username=username), 400

    try:
        add_to_db(username, hashing_a_pass(password))
    except sqlite3.IntegrityError:
        flash('That username is already taken.', 'error')
        return render_template('register.html', username=username), 409

    flash('Account created. Sign in with your master password.', 'success')
    return redirect(url_for('login_page'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been signed out.', 'info')
    return redirect(url_for('login_page'))


# --- Vault -----------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():
    entry_count = count_passwords(session['username'])
    return render_template('dashboard.html', entry_count=entry_count)


@app.route('/vault', methods=['GET'])
@login_required
def vault():
    return render_template('viewsaved.html', entry_count=count_passwords(session['username']))


@app.route('/vault', methods=['POST'])
@login_required
def vault_unlock():
    username = session['username']
    master_pass = request.form.get('master_password', '')
    stored_hash = get_user(username)
    if not (stored_hash and check_pass(master_pass, stored_hash)):
        flash('Master password is incorrect.', 'error')
        return render_template('viewsaved.html', entry_count=count_passwords(username)), 401

    key = derive_key(master_pass, get_user_salt(username))
    entries = []
    for site_name, value, entry_id in get_passwords(username):
        if is_encrypted(value):
            try:
                plaintext = decrypt_secret(key, value)
            except InvalidToken:
                # Encrypted under a different master password; can't recover here.
                plaintext = None
        else:
            # Entry saved before encryption existed — encrypt it now.
            plaintext = value
            update_password_value(entry_id, username, encrypt_secret(key, value))
        entries.append({'id': entry_id, 'site': site_name, 'password': plaintext})

    return render_template('viewsaved.html', passwords=entries, entry_count=len(entries))


@app.route('/vault/new', methods=['GET'])
@login_required
def new_entry_page():
    return render_template('passwordcreate.html')


@app.route('/vault/new', methods=['POST'])
@login_required
def new_entry():
    username = session['username']
    master_pass = request.form.get('master_password', '')
    site_name = request.form.get('site_name', '').strip()
    new_pass = request.form.get('password', '')

    if not site_name or not new_pass:
        flash('Site name and password are both required.', 'error')
        return render_template('passwordcreate.html', site_name=site_name), 400

    stored_hash = get_user(username)
    if not (stored_hash and check_pass(master_pass, stored_hash)):
        flash('Master password is incorrect.', 'error')
        return render_template('passwordcreate.html', site_name=site_name), 401

    key = derive_key(master_pass, get_user_salt(username))
    save_password(username, site_name, encrypt_secret(key, new_pass))
    flash(f'Entry for “{site_name}” saved to your vault.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/vault/delete', methods=['POST'])
@login_required
def vault_delete():
    entry_id = request.form.get('id', '')
    if delete_password(entry_id, session['username']):
        flash('Entry deleted.', 'success')
    else:
        flash('Entry not found.', 'error')
    return redirect(url_for('vault'))


@app.route('/generator')
@login_required
def generator():
    return render_template('passwordgen.html')


# --- Legacy paths from the previous version --------------------------------

@app.route('/create-account')
def legacy_create_account():
    return redirect(url_for('register_page'))


@app.route('/loggout')
def legacy_loggout():
    return redirect(url_for('logout'))


@app.route('/createpass')
def legacy_createpass():
    return redirect(url_for('new_entry_page'))


@app.route('/viewsaved')
def legacy_viewsaved():
    return redirect(url_for('vault'))


@app.route('/passwordgen')
def legacy_passwordgen():
    return redirect(url_for('generator'))


if __name__ == '__main__':
    app.run(debug=True)
