"""
Package containig the classes related to the Manager of Ceryx.
"""
from flask import Flask
from whitenoise import WhiteNoise

from ceryx.api import CeryxApi
from ceryx.docker import DockerApi

app = Flask(__name__)
app.config.from_object('ceryx.settings')
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

CERYX = CeryxApi.from_config()
DOCKER = DockerApi.from_config()

from ceryx.manager import views
