import re

import flask_login

from ceryx.manager import router, users, docker_api


class User(flask_login.UserMixin):

    def __init__(self, username):
        self.username = username

    def get_id(self):
        return self.username

    @staticmethod
    def login(username, password):
        return User(username) if users.login(username, password) else None

    @staticmethod
    def get(username):
        u = users.lookup(username)
        if not u:
            return None

        return User(u[0])

    @staticmethod
    def all():
        for user in users.lookup():
            yield User(user)
    
    @staticmethod
    def insert(username, plain_password):
        users.insert(username, plain_password)
        return User(username)
    
    @staticmethod
    def update(username, new_password):
        return User.insert(username, new_password)
    
    @staticmethod
    def delete(username):
        users.delete(username)


class Route:
    DEFAULT_PATH = '/'
    DEFAULT_PORT = 80

    def __init__(self, host, path, target, port, is_orphan=False):
        self.host = host
        self.path = path
        self.target = target
        self.port = port
        self.is_orphan = is_orphan
    
    def update(self, host, path, target, port):
        old_source = f'{self.host}:{self.path}'
        new_source = f'{host}:{path}'

        if isinstance(port, str):
            port = int(port)
        
        if port is not None and port != Route.DEFAULT_PORT:
            target = f'{target}:{port}'

        router.update(old_source, new_source, target)

        return Route(host, path, target, port)

    @staticmethod
    def _is_orphan(route, services):
        for s in services:
            if re.match(s.name + r'(:\d+?)?$', route["target"]):
                return False
        return True

    @staticmethod
    def _parse(route, services):
        source_path = route['source'].split(':')
        source = source_path[0]
        path = source_path[1]

        target_port = route['target'].split(':')
        target = target_port[0]
        port = Route.DEFAULT_PORT if len(target_port) < 2 else target_port[1]

        is_orphan = Route._is_orphan(route, services)

        return Route(source, path, target, port, is_orphan)

    @staticmethod
    def all():
        services = docker_api.services()
        routes = router.lookup_routes('*')

        routes = [Route._parse(r, services) for r in routes]
        return sorted(routes, key=lambda r: r.host + r.path)

    @staticmethod
    def add(route):
        source = route.host
        if route.path is not None:
            source = f'{source}:{route.path}'

        if route.port != Route.DEFAULT_PORT:
            target = f'{route.target}:{route.port}'
        else:
            target = route.target

        router.insert(source, target)

    @staticmethod
    def get(host, path):
        target = router.lookup(f'{host}:{path}')
        if target is None:
            raise Route.NotFound()

        services = docker_api.services()
        route = {
            'source': f'{host}:{path}',
            'target': target
        }
        return Route._parse(route, services)

    @staticmethod
    def delete(route):
        if isinstance(route, Route):
            route = f'{route.host}:{route.path}'
        router.delete(route)

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
