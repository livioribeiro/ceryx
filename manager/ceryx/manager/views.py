import json

from flask import abort, flash, redirect, request, render_template, url_for
from flask_login import login_required, login_user, logout_user

from . import app, users, router
from .forms import RouteForm, RouteDeleteForm, LoginForm, UserAddForm, UserEditForm
from .models import User, Route, Service


@app.errorhandler(Route.NotFound)
def handle_route_not_found(e):
    abort(404)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username, password = form.username.data, form.password.data
        user = User.login(username, password)
        if user:
            login_user(user)
            return redirect(url_for('list_routes'))
        else:
            flash('Incorrect email or password', 'error')

    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/services', methods=['GET'])
@login_required
def list_services():
    services = Service.all()
    return render_template('services/list.html', services=services)


@app.route('/', methods=['GET'])
def index_redirect():
    return redirect(url_for('list_routes'))


@app.route('/routes', methods=['GET'])
@login_required
def list_routes():
    routes = Route.all()
    return render_template('routes/list.html', routes=routes)


@app.route('/routes/orphaned')
@login_required
def orphaned_routes():
    routes = Route.all()
    orphaned = [r for r in routes if r.is_orphan]
    return render_template('routes/orphaned.html', routes=orphaned)


@app.route('/routes/new', methods=['GET', 'POST'])
@login_required
def route_add():
    services = Service.all()
    form = RouteForm()
    form.target.choices = [(s.name, s.name) for s in services]

    if form.validate_on_submit():
        route = Route(form.host.data,
                      form.path.data,
                      form.target.data,
                      form.port.data)

        try:
            Route.add(route)
            flash(f'Route "{route.host}{route.path}" added', 'success')
            return redirect(url_for('list_routes'))
        except Exception as e:
            app.logger.error(e)
            flash(f'Failed to add route "{route.host}{route.path}"')

    return render_template('routes/new.html', form=form)


@app.route('/routes/edit/<path:route>', methods=['GET', 'POST'])
@login_required
def route_edit(route):
    idx = route.index('/')
    host, path = route[:idx], route[idx:]

    route = None
    try:
        route = Route.get(host, path)
    except Route.NotFound:
        abort(404)

    services = Service.all()
    form = RouteForm(obj=route)
    form.target.choices = [(s.name, s.name) for s in services]

    if form.validate_on_submit():
        try:
            route = route.update(form.host.data,
                                 form.path.data,
                                 form.target.data,
                                 form.port.data)

            flash(f'Route "{route.host}{route.path}" updated', 'success')
            return redirect(url_for('list_routes'))
        except Exception as e:
            app.logger.error(e)
            flash(f'Failed to update route "{route.host}{route.path}"')

    return render_template('routes/edit.html', form=form)


@app.route('/routes/delete/<path:route>', methods=['POST'])
@login_required
def route_delete(route):
    idx = route.index('/')
    host, path = route[:idx], route[idx:]
    route = f'{host}:{path}'

    try:
        Route.delete(route)
        flash(f'Route "{host}{path}" deleted', 'success')
    except Exception as e:
        app.logger.error(e)
        flash(f'Could not delete route {host}{path}', 'error')
    
    return redirect(url_for('list_routes'))


@app.route('/users', methods=['GET'])
@login_required
def list_users():
    users = User.all()
    return render_template('users/list.html', users=users)


@app.route('/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    form = UserAddForm()
    if form.validate_on_submit():
        user = User.insert(form.username.data, form.password.data)
        flash(f'User "{user.username}" added', 'success')
        return redirect(url_for('list_users'))

    return render_template('users/new.html', form=form)


@app.route('/users/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(username):
    if not User.get(username):
        abort(404)

    form = UserEditForm()

    if form.validate_on_submit():
        password = form.password.data
        User.update(username, password)
        flash(f'User "{username}" updated', 'success')
        return redirect(url_for('list_users'))

    return render_template('users/edit.html', form=form)


@app.route('/users/<username>/delete', methods=['POST'])
@login_required
def delete_user(username):
    if not User.get(username):
        return abort(404)

    User.delete(username)
    flash(f'User "{namename}" deleted', 'success')

    return redirect(url_for('list_users'))
