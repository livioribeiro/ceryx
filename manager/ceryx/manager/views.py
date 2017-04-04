import json

from flask import abort, flash, redirect, request, render_template, url_for

from . import app, CERYX, DOCKER
from .forms import RouteForm
from .models import Route, Service
from ceryx.api import RouteNotFoundError


@app.errorhandler(RouteNotFoundError)
def handle_route_not_found(e):
    abort(404)

@app.route('/services', methods=['GET'])
def list_services():
    services = Service.all()
    return render_template('services/list.html', services=services)


@app.route('/routes', methods=['GET'])
def list_routes():
    routes = Route.all()
    return render_template('routes/list.html', routes=routes)


@app.route('/routes/orphaned')
def orphaned_routes():
    routes = Route.all()
    orphaned = [r for r in routes if r.is_orphan]
    return render_template('routes/orphaned.html', routes=orphaned)


@app.route('/routes/new', methods=['GET', 'POST'])
def new_route():
    services = Service.all()
    form = RouteForm()
    form.target.choices = [(s.name, s.name) for s in services]

    if form.validate_on_submit():
        route = Route(form.source.data, form.target.data)
        Route.add(route)

        flash(f'Route "{route.source} -> {route.target}" added')
        return redirect(url_for('list_routes'))

    return render_template('routes/form.html', form=form)


@app.route('/routes/<path:route>/delete', methods=['POST'])
def delete_route(route):
    if route != request.form['route']:
        abort(400)
    
    Route.delete(route)

    return redirect(url_for('list_routes'))
