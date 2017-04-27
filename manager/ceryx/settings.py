"""
Settings file, which is populated from the environment while enforcing common
use-case defaults.
"""
import os

DEBUG = True
if os.getenv('CERYX_DEBUG', '').lower() in ['0', 'no', 'false']:
    DEBUG = False

WEB_BIND_HOST = os.getenv('CERYX_WEB_HOST', '127.0.0.1')
WEB_BIND_PORT = os.getenv('CERYX_WEB_PORT', 8080)

SECRET_KEY = os.getenv('CERYX_SECRET_KEY')
if SECRET_KEY:
    with open(SECRET_KEY, 'r') as f:
        SECRET_KEY = f.read()

REDIS_HOST = os.getenv('CERYX_REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.getenv('CERYX_REDIS_PORT', 6379)
REDIS_PREFIX = os.getenv('CERYX_REDIS_PREFIX', 'ceryx')

DOCKER_HOST = os.getenv('CERYX_DOCKER_HOST', 'unix:///var/run/docker.sock')
DOCKER_PORT = os.getenv('CERYX_DOCKER_PORT')

PROXY_NETWORK = os.getenv('CERYX_PROXY_NETWORK', 'proxy')
