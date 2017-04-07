"""
Package containing a service to interact with the Ceryx api
"""

import requests

from ceryx import settings


class RouteNotFoundError(Exception):
    def __init__(self, route):
        super().__init__(f'Route: {route}')
        self.route = route


class CeryxApiService:
    """Interacts with the Ceryx Api"""

    @staticmethod
    def from_config():
        """
        Creates an instance of ``CeryxService`` from settings settings.
        """
        return CeryxApiService(settings.CERYX_API_HOST, settings.CERYX_API_PORT)

    def __init__(self, host, port):
        self.api_url = f'http://{host}:{port}/api'

        session = requests.Session()
        session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
        self.session = session

    def routes(self):
        """Fetches all the routes"""
        res = self.session.get(f'{self.api_url}/routes')
        res.raise_for_status()
        return res.json()

    def route(self, name):
        """Fetches the route with the given name
        
        If the route does not exist, return None
        """
        res = self.session.get(f'{self.api_url}/routes/{name}')
        if res.status_code == requests.codes.not_found:
            return None
        
        res.raise_for_status()

        return res.json()

    def has_route(self, name):
        """Checks if a route exists"""
        route = self.route(name)
        return route is not None

    def add_route(self, source, target):
        """Adds a new route"""
        data = {'target': target}

        res = self.session.put(f'{self.api_url}/routes/{source}', json=data)
        res.raise_for_status()

        return res.json()

    def delete_route(self, source):
        """Deletes a route
        
        If the route does not exist, raise RouteNotFoundError
        """
        res = self.session.delete(f'{self.api_url}/routes/{source}')
        if res.status_code == requests.codes.not_found:
            raise RouteNotFoundError(source)

        res.raise_for_status()