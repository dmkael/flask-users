from flask import Flask, session, request
from flask import redirect, render_template, url_for, flash
from flask import get_flashed_messages
from validator import validate
from users_db import UsersRepo
from hashlib import sha256

app = Flask(__name__)
app.config['SECRET_KEY'] = 'some_secret'


users_logins = [
    {'name': 'tota', 'password': sha256(b'password123').hexdigest()},
    {'name': 'alice', 'password': sha256(b'donthackme').hexdigest()},
    {'name': 'bob', 'password': sha256(b'qwerty').hexdigest()},
    {'name': 'ADMIN', 'password': sha256(b'admin').hexdigest()}
]


@app.get('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    user = session.get('user')
    if not user:
        return render_template(
            "index.html",
            messages=messages
        ), 401
    return redirect(url_for('get_users', user=user), 302)


@app.post('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
    return redirect(url_for('index'), 302)


def get_user(form_data, repo):
    name = form_data['username']
    # password = sha256(form_data['password'].encode()).hexdigest()
    # for user in repo:
    #     if user['name'] == name and user['password'] == password:
    #         return name
    return name


@app.post('/users')
def authorize_user():
    user = get_user(request.form.to_dict(), users_logins)
    if user:
        session['user'] = user
        repo = UsersRepo(user)
        return render_template(
            'users/index.html',
            username=user,
            user_db=repo.content()
        )
    flash('Invalid login or password')
    return redirect(url_for('index'))


@app.get('/users')
def get_users():
    username = session.get('user')
    if username is None:
        return 'Access denied', 401
    repo = UsersRepo(username)
    term = request.args.get('term', '')
    items = repo.content().items()
    filtered_usr = {i: u for i, u in items if term.lower() in u['name'].lower()}
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'users/index.html',
        username=username,
        user_db=filtered_usr,
        messages=messages,
        search=term
    )


@app.get('/new_user')
def get_new_user():
    errors = {}
    username = session.get('user')
    if username is None:
        return 'Access denied', 401
    return render_template(
        'users/new_user.html',
        username=username,
        errors=errors
    )


@app.post('/new_user')
def post_new_user():
    data = request.form.to_dict()
    username = session.get('user')
    if username is None:
        return 'Access denied', 401
    repo = UsersRepo(username)
    errors = validate(data, repo.content())
    if errors:
        return render_template(
            'users/new_user.html',
            username=username,
            errors=errors
        )
    repo.save_user(user=data)
    flash('User created', 'success')
    return redirect(url_for('get_users'), 302)


@app.get('/users/<user_id>')
def edit_user(user_id):
    username = session.get('user')
    if username is None:
        return 'Access denied', 401
    repo = UsersRepo(username)
    user = repo.find(user_id)
    errors = {}
    return render_template(
        'users/edit_user.html',
        username=username,
        user=user,
        errors=errors,
        user_id=user_id
    )


@app.post('/users/<user_id>/edit')
def post_edited_user(user_id):
    username = session.get('user')
    if username is None:
        return 'Access denied', 401
    repo = UsersRepo(username)
    user = repo.find(user_id)
    data = request.form.to_dict()
    errors = validate(data, repo.content(), user_id)
    if errors:
        return render_template(
            'users/edit_user.html',
            username=username,
            user=user,
            errors=errors,
            user_id=user_id
        )
    if user != data:
        repo.save_user(user=data, user_id=user_id)
        flash('User updated', 'success')
    return redirect(url_for('get_users'), 302)


@app.route('/users/<user_id>/delete', methods=['POST', 'DELETE'])
def delete_user(user_id):
    username = session.get('user')
    if username is None:
        return 'Access denied', 401
    repo = UsersRepo(username)
    user = repo.find(user_id)['name']
    repo.delete_user(user_id)
    flash(f'User "{user}" deleted', 'success')
    return redirect(url_for('index'), 302)
