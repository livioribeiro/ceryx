"""
Package containig the classes related to the Manager of Ceryx.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from whitenoise import WhiteNoise

from ceryx.ceryx_service import CeryxApiService
from ceryx.docker_service import DockerService

app = Flask(__name__)
app.config.from_object('ceryx.settings')
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from ceryx.manager.models import User
    return User.query.get(int(user_id))

ceryx_api = CeryxApiService.from_config()
docker_api = DockerService.from_config()

from ceryx.manager import views
