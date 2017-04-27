"""
Package containing a service to interact with the Docker api
"""

import docker

from ceryx import settings


class DockerService:
    """Interacts with the Docker Api"""

    @staticmethod
    def from_config():
        """Create an instance of ``DockerService`` from settings"""
        return DockerService(settings.DOCKER_HOST, settings.PROXY_NETWORK)

    def __init__(self, base_url, proxy_network):
        self.client = docker.DockerClient(base_url=base_url, version='auto')
        self.proxy_network = proxy_network

    def _is_in_proxy_network(self, service):
        if 'Networks' not in service.attrs['Spec']:
            return False

        for net in service.attrs['Spec']['Networks']:
            if net['Target'] == self.proxy_network:
                return True

        return False

    def services(self, filters=None):
        """Get services from docker daemon"""
        filters = filters or dict()
        services = self.client.services.list(filters=filters)
        return [s for s in services if self._is_in_proxy_network(s)]

    def has_service(self, name):
        """Checks if a service with the given exists"""
        services = self.services(filters={'name': name})
        return len(services) > 0
