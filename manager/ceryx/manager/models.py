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
    def __init__(self, source, target, is_orphan=False):
        self.source = source
        self.target = target
        self.is_orphan = is_orphan

    @staticmethod
    def all():
        services = docker_api.services()
        routes = ceryx_api.routes()

        def is_orphan(route):
            for s in services:
                if s.name == route['target']:
                    return False
            return True

        return [Route(r['source'], r['target'], is_orphan(r)) for r in routes]

    @staticmethod
    def add(route):
        ceryx_api.add_route(route.source, route.target)

    @staticmethod
    def get(source):
        route = ceryx_api.route(source)
        if route is None:
            raise Route.NotFound()

        return Route(route['source'], route['target'])

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
        ports = service.attrs['Endpoint']['Ports']

        return Service(name, image, ports)

    def __init__(self, name, image, ports):
        self.name = name
        self.image = image
        self.ports = ports

    @property
    def target_port(self):
        return self.ports[0]['TargetPort']

    @property
    def published_port(self):
        return self.ports[0]['PublishedPort']

    @staticmethod
    def all():
        def is_published(service):
            attrs = service.attrs
            return 'Ports' in attrs['Endpoint'] and attrs['Endpoint']['Ports']

        services = docker_api.services()
        return [Service.from_docker_obj(s) for s in services if is_published(s)]
