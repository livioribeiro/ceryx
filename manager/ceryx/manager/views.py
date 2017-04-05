import json

from flask import abort, flash, redirect, request, render_template, url_for
from flask_login import login_required, login_user

from . import app
from .forms import RouteForm, LoginForm
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
            flash('Incorrect email or password')
    
    return render_template('login.html', form=form)


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
        Route.add(route)

        flash('Route "{} -> {}" added'.format(route.source, route.target))
        return redirect(url_for('list_routes'))

    return render_template('routes/form.html', form=form)


@app.route('/routes/<path:route>/delete', methods=['POST'])
@login_required
def delete_route(route):
    if route != request.form['route']:
        abort(400)
    
    Route.delete(route)

    return redirect(url_for('list_routes'))
