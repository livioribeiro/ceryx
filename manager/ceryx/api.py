import requests

from ceryx import settings


class CeryxApi:
    """
    Interacts with the Ceryx Api
    """

    @staticmethod
    def from_config():
        """
        Returns a CeryxApi, using the default configuration from Ceryx
        settings.
        """
        return CeryxApi(settings.CERYX_API_HOST, settings.CERYX_API_PORT)

    def __init__(self, host, port):
        self.api_url = f'http://{host}:{port}/api'

        session = requests.Session()
        session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
        self.session = session

    def routes(self):
        """
        Fetches all the routes
        """
        return self.session.get(f'{self.api_url}/routes').json()
    
    def add_route(self, source, target):
        data = {'source': source, 'target': target}
        
        res = self.session.post(f'{self.api_url}/routes', json=data)
        res.raise_for_status()

        return res.json()
