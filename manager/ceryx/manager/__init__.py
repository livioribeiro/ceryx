"""
Package containig the classes related to the Manager of Ceryx.
"""
from flask import Flask
from flask_login import LoginManager
from whitenoise import WhiteNoise

from ceryx.docker import DockerService
from ceryx.db import RedisRouter, RedisUsers

app = Flask(__name__)
app.config.from_object('ceryx.settings')
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from ceryx.manager.models import User
    return User.get(user_id)

docker_api = DockerService.from_config()
router = RedisRouter.from_config()
users = RedisUsers.from_config()

from ceryx.manager import views
