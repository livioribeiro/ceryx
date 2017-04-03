import json

from flask import abort, flash, redirect, request, render_template, url_for

from ceryx.api import CeryxApi
from ceryx.dock import DockerApi

from . import app

api = CeryxApi.from_config()
dock = DockerApi.from_config()


@app.route('/services', methods=['GET'])
def list_services():
    services = dock.services()
    return render_template('services/list.html', services=services)


@app.route('/routes', methods=['GET'])
def list_routes():
    routes = api.routes()
    return render_template('routes/list.html', routes=routes)


@app.route('/routes/new', methods=['GET'])
def new_route():
    services = dock.services()
    return render_template('routes/new.html', services=services)


@app.route('/routes/new', methods=['POST'])
def create_route():
    source = request.form['source']
    target = request.form['target']

    api.add_route(source, target)
    flash(f'Route "{source}" added')

    return redirect(url_for('list_routes'))
