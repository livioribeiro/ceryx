import bcrypt
import flask_login

from ceryx.manager import db, ceryx_api, docker_api


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    name = db.Column(db.String(80))

    def __init__(self, email, name):
        self.email = email
        self.name = name
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
        self.password = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt())

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
        if isinstance(route, Route):
            ceryx_api.delete_route(route.source)
        else: # is str
            ceryx_api.delete_route(route)
    
    class NotFound(Exception):
        pass


class Service:
    def __init__(self, name, ports):
        self.name = name
        self.ports = ports
    
    @staticmethod
    def all():
        services = docker_api.services()
        return [Service(s.name, s.attrs['Endpoint']['Ports']) for s in services]
