"""
Settings file, which is populated from the environment while enforcing common
use-case defaults.
"""
import os

NAME = os.getenv('CERYX_NAME', 'ceryx-manager')
DEBUG = True
if os.getenv('CERYX_DEBUG', '').lower() in ['0', 'no', 'false']:
    DEBUG = False

WEB_BIND_HOST = os.getenv('CERYX_WEB_HOST', '127.0.0.1')
WEB_BIND_PORT = os.getenv('CERYX_WEB_PORT', 8080)

CERYX_API_HOST = os.getenv('CERYX_API_HOST', 'ceryx-api')
CERYX_API_PORT = os.getenv('CERYX_API_PORT', 5555)

SERVER_NAME = os.getenv('CERYX_SERVER_NAME')

SECRET_KEY = os.getenv('CERYX_SECRET_KEY')
if SECRET_KEY:
    with open(SECRET_KEY, 'r') as f:
        SECRET_KEY = f.read()

DOCKER_HOST = os.getenv('CERYX_DOCKER_HOST', 'unix:///var/run/docker.sock')
DOCKER_PORT = os.getenv('CERYX_DOCKER_PORT')

PROXY_NETWORK = os.getenv('CERYX_PROXY_NETWORK', 'proxy')

SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///:memory:')
SQLALCHEMY_TRACK_MODIFICATIONS = False