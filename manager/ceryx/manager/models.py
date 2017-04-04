from . import CERYX, DOCKER
from ceryx.api import RouteNotFoundError


class Route:
    def __init__(self, source, target, is_orphan=False):
        self.source = source
        self.target = target
        self.is_orphan = is_orphan

    @staticmethod
    def all():
        services = DOCKER.services()
        routes = CERYX.routes()

        def is_orphan(route):
            for s in services:
                if s['name'] == route['target']:
                    return False
            return True

        return [Route(r['source'], r['target'], is_orphan(r)) for r in routes]
    
    @staticmethod
    def add(route):
        CERYX.add_route(route.source, route.target)
    
    @staticmethod
    def get(source):
        try:
            route = CERYX.route(source)
            return Route(route['source'], route['target'])
        except RouteNotFoundError:
            return None
    
    @staticmethod
    def delete(route):
        if isinstance(route, Route):
            CERYX.delete_route(route.source)
        else: # is str
            CERYX.delete_route(route)


class Service:
    def __init__(self, name, ports):
        self.name = name
        self.ports = ports
    
    @staticmethod
    def all():
        services = DOCKER.services()
        return [Service(s['name'], s['ports']) for s in services]
