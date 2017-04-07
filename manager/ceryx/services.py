"""
Package containing services used to interact with the Ceryx Api and Docker
"""
import docker
import requests

from ceryx import settings


class DockerService:
    """Interacts with the Docker Api"""

    @staticmethod
    def from_config():
        """Create an instance of ``DockerService`` from settings"""
        return DockerService(settings.DOCKER_HOST, settings.PROXY_NETWORK)

    def __init__(self, base_url, proxy_network):
        self.client = docker.DockerClient(base_url=base_url)
        self.proxy_network = proxy_network

    def _is_in_proxy_network(self, service):
        if 'Networks' not in service.attrs['Spec']:
            return False

        for net in service.attrs['Spec']['Networks']:
            if net['Target'] == self.proxy_network:
                return True

        return False

    def _has_published_ports(self, service):
        if 'Ports' not in service.attrs['Endpoint']:
            return False
        return True

    def _is_published(self, service):
        return self._is_in_proxy_network(service) \
            and self._has_published_ports(service)

    def services(self, filters=None):
        """Get services from docker daemon"""
        filters = filters or dict()
        services = self.client.services.list(filters=filters)
        return [s for s in services if self._is_published(s)]

    def has_service(self, name):
        """Checks if a service with the given exists"""
        services = self.services(filters={'name': name})
        return len(services) > 0


class CeryxApiService:
    """Interacts with the Ceryx Api"""

    @staticmethod
    def from_config():
        """
        Creates an instance of ``CeryxService`` from settings settings.
        """
        return CeryxApiService(settings.CERYX_API_HOST, settings.CERYX_API_PORT)

    def __init__(self, host, port):
        self.api_url = 'http://{}:{}/api'.format(host, port)

        session = requests.Session()
        session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
        self.session = session

    def routes(self):
        """Fetches all the routes"""
        return self.session.get(self.api_url + '/routes').json()

    def route(self, name):
        """Fetches the route with the given name"""
        res = self.session.get(self.api_url + '/routes/' + name)
        if res.status_code == requests.codes.not_found:
            return None

        return res.json()

    def has_route(self, name):
        """Checks if a route exists"""
        res = self.session.get(self.api_url + '/routes/' + name)
        return res.status_code == requests.codes.ok

    def add_route(self, source, target):
        """Adds a new route"""
        data = {'target': target}

        res = self.session.put(self.api_url + '/routes/' + source, json=data)
        res.raise_for_status()

        return res.json()

    def delete_route(self, source):
        """Deletes a route"""
        res = self.session.delete(self.api_url + '/routes/' + source)
        
        status = res.status_code
        if status == requests.codes.ok:
            return True

        if status == requests.codes.not_found:
            return None
        
        return False
