import re

import bcrypt
import flask_login

from ceryx.manager import db, ceryx_api, docker_api


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))

    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.password = None

    @staticmethod
    def login(email, plain_password):
        user = User.query.filter_by(email=email).first()
        if user is not None:
            password = user.password.encode()
            plain_password = plain_password.encode()
            return user if bcrypt.checkpw(plain_password, password) else None

        return None

    def set_password(self, plain_password):
        hashed_password = bcrypt.hashpw(plain_password.encode(),
                                        bcrypt.gensalt())

        self.password = hashed_password.decode('utf-8')

    def __repr__(self):
        return '<User %r (%r)>' % self.name, self.email


class Route:
    DEFAULT_PORT = 80

    def __init__(self, source, target, port, is_orphan=False):
        self.source = source
        self.target = target
        self.port = port
        self.is_orphan = is_orphan

    @staticmethod
    def _is_orphan(route, services):
        for s in services:
            if re.match(s.name + r'(:\d+?)?$', route["target"]):
                return False
        return True

    @staticmethod
    def _from_api(route, services):
        source = route['source']
        target_port = route['target'].split(':')
        target = target_port[0]
        port = Route.DEFAULT_PORT if len(target_port) < 2 else target_port[1]

        return Route(source, target, port, Route._is_orphan(route, services))


    @staticmethod
    def all():
        services = docker_api.services()
        routes = ceryx_api.routes()

        return [Route._from_api(r, services) for r in routes]

    @staticmethod
    def add(route):
        source = route.source

        if route.port != Route.DEFAULT_PORT:
            target = f'{route.target}:{route.port}'
        else:
            target = route.target

        ceryx_api.add_route(source, target)

    @staticmethod
    def get(source):
        route = ceryx_api.route(source)
        if route is None:
            raise Route.NotFound()

        services = docker_api.services()
        return Route._from_api(route, services)

    @staticmethod
    def delete(route):
        route = route.source if isinstance(route, Route) else route
        ceryx_api.delete_route(route)

    class NotFound(Exception):
        pass


class Service:
    @staticmethod
    def from_docker_obj(service):
        name = service.name
        image = service.attrs['Spec']['TaskTemplate']['ContainerSpec']['Image']
        image = image.split('@')[0]

        return Service(name, image)

    def __init__(self, name, image):
        self.name = name
        self.image = image

    @staticmethod
    def all():
        services = docker_api.services()
        return [Service.from_docker_obj(s) for s in services]
