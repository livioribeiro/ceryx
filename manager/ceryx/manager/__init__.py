"""
Package containig the classes related to the Manager of Ceryx.
"""
from flask import Flask
from whitenoise import WhiteNoise

app = Flask(__name__)
app.config.from_object('ceryx.settings')
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

from ceryx.manager import views
