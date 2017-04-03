import docker

from ceryx import settings


class DockerApi:
    @staticmethod
    def from_config():
        """Create an instance of ``DockerApi`` from settings"""
        return DockerApi(settings.DOCKER_HOST)

    def __init__(self, base_url):
        self.client = docker.DockerClient(base_url=base_url)

    def _parse_service(self, service):
        if 'Ports' not in service.attrs['Endpoint']:
            raise Exception(f'Service "{service.name}" is not published')
        
        name = service.name
        ports = service.attrs['Endpoint']['Ports']

        return {'name': name, 'ports': ports}

    def services(self):
        """Get services from docker daemon"""
        services = self.client.services.list()
        return [self._parse_service(serv) for serv in services if 'Ports' in serv.attrs['Endpoint']]
