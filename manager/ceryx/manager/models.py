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


class RouteMapping:
    DEFAULT_PATH = '/'
    DEFAULT_PORT = 80

    def __init__(self, route, path, target, port, is_orphan=False):
        self.route = route
        self.path = path
        self.target = target
        self.port = port
        self.is_orphan = is_orphan

    @staticmethod
    def _is_orphan(target, services):
        for s in services:
            if re.match(s.name + r'(:\d+?)?$', target):
                return False
        return True

    @staticmethod
    def parse(services, route, path, target):
        target_port = target.split(':')
        target = target_port[0]
        port = Route.DEFAULT_PORT if len(target_port) < 2 else target_port[1]

        is_orphan = RouteMapping._is_orphan(route, services)

        return RouteMapping(route, path, target, port)

    def update(self, path, target, port):
        if isinstance(port, str):
            port = int(port)
        
        if port is not None and port != Route.DEFAULT_PORT:
            target = f'{target}:{port}'
        
        router.update_path(self.route.host, path, target)
        self.path = path
        self.target = target
        self.port = port


class Route:
    DEFAULT_PATH = '/'
    DEFAULT_PORT = 80

    def __init__(self, host, paths):
        self.host = host
        self.paths = paths
    
    def update(self, host):
        router.update_host(self.host, host)
        self.host = host

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

        route_list = []
        for r in routes:
            host = r['host']
            paths = [RouteMapping.parse(services, host, p, t) for p, t in r['paths'].items()]
            paths = sorted(paths, key=lambda p: p.path + p.target)
            route_list.append(Route(host, paths))

        return sorted(route_list, key=lambda r: r.host)

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
