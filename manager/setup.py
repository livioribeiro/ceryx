from setuptools import setup

setup(
    name='ceryx',
    version='0.2.0',
    author='Livio Ribeiro',
    author_email=('Livio Ribeiro <livioribeiro@outlook.com>'),
    packages=['ceryx', 'ceryx.manager'],
    include_package_data=True,
    url='https://pypi.python.org/sourcelair/ceryx/',
    license=open('LICENSE.txt').read(),
    description='Ceryx, a dynamic reverse proxy based on NGINX OpenResty.',
    long_description=open('README.md').read(),
    install_requires=[
        'docker==2.2.1',
        'Flask==0.12',
        'requests==2.13.0',
        'gunicorn==19.7.1',
        'whitenoise==3.3.0',
    ],
)

from distutils.core import setup
