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
        return DockerService(settings.DOCKER_HOST)

    def __init__(self, base_url):
        self.client = docker.DockerClient(base_url=base_url)

    def services(self):
        """Get services from docker daemon"""
        return self.client.services.list()

    def has_service(self, name):
        """Checks if a service with the given exists"""
        services = self.client.services.list(filters={'name': name})
        return len(services) > 0


class CeryxApiService:
    """Interacts with the Ceryx Api"""

    @staticmethod
    def from_config():
        """
        Creates an instance of ``CeryxService`` from settings
        settings.
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
        res = self.session.get(self.api_url + '/routes/{name}')
        if res.status_code == requests.codes.not_found:
            return None
        
        return res.json()
    
    def has_route(self, name):
        """Checks if a route exists"""
        res = self.session.get(self.api_url + '/routes/{name}')
        return res.status_code == requests.codes.ok

    def add_route(self, source, target):
        data = {'source': source, 'target': target}
        
        res = self.session.post(self.api_url + '/routes', json=data)
        res.raise_for_status()

        return res.json()
    
    def delete_route(self, source):
        self.session.delete(self.api_url + '/routes/{source}')
