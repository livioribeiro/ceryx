import json

from flask import abort, flash, redirect, request, render_template, url_for
from flask_login import login_required, login_user, logout_user

from . import app, db
from .forms import RouteForm, LoginForm, UserAddForm, UserEditForm
from .models import User, Route, Service


@app.errorhandler(Route.NotFound)
def handle_route_not_found(e):
    abort(404)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.login(form.email.data, form.password.data)
        if user is not None:
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
def new_route():
    services = Service.all()
    form = RouteForm()
    form.target.choices = [(s.name, s.name) for s in services]

    if form.validate_on_submit():
        route = Route(form.source.data, form.target.data)

        try:
            Route.add(route)
            flash(f'Route "{route.source}" added', 'success')
            return redirect(url_for('list_routes'))
        except Exception as e:
            app.logging.error(e)
            flash('Failed to add route')

    return render_template('routes/new.html', form=form)


@app.route('/routes/<path:route>/delete', methods=['POST'])
@login_required
def delete_route(route):
    if route != request.form['route']:
        abort(400)

    try:
        Route.delete(route)
        flash(f'Route "{route}" deleted', 'success')
    except Exception as e:
        app.logging.error(e)
        flash(f'Could not delete route {route}', 'error')

    return redirect(url_for('list_routes'))


@app.route('/users', methods=['GET'])
@login_required
def list_users():
    users = User.query.all()
    return render_template('users/list.html', users=users)


@app.route('/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    form = UserAddForm()
    if form.validate_on_submit():
        user = User(form.name.data, form.email.data)
        user.set_password(form.password.data)

        session = db.session

        try:
            session.add(user)
            session.commit()
            flash(f'User "{user.name}" added', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            session.rollback()
            app.logging.error(e)
            flash('Failed to add user', 'error')

    return render_template('users/new.html', form=form)


@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        if form.password.data:
            user.set_password(form.password.data)

        session = db.session

        try:
            session.add(user)
            session.commit()
            flash(f'User "{user.name}" updated', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            session.rollback()
            app.logging.error(e)
            flash('Failed to edit user', 'error')

    return render_template('users/edit.html', form=form)


@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.email != request.form['email']:
        return abort(400)

    session = db.session

    try:
        session.delete(user)
        session.commit()
        flash(f'User "{user.name}" deleted', 'success')
    except Exception as e:
        session.rollback()
        app.logging.error(e)
        flash('Failed to delete user', 'error')

    return redirect(url_for('list_users'))
