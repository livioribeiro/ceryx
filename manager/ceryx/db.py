"""
Simple Redis client, implemented the data logic of Ceryx.
"""
import redis
import bcrypt

from ceryx import settings


REDIS_DEFAULT_DB = 0


class RedisRouter:
    """
    Router using a redis backend, in order to route incoming requests.
    """

    class LookupNotFound(Exception):
        """
        Exception raised when a lookup for a specific host was not found.
        """
        def __init__(self, message, errors=None):
            Exception.__init__(self, message)
            if errors is None:
                self.errors = {'message': message}
            else:
                self.errors = errors
    
    class HostExists(Exception):
        """
        Exception raised when trying to update a host mapping to a key
        that already exists in the database
        """
        pass
    
    class PathExists(Exception):
        """
        Exception raised when trying to update a path to a key that
        already exists in the hashmap
        """
        pass

    @staticmethod
    def from_config(path=None):
        """
        Returns a RedisRouter, using the default configuration from Ceryx
        settings.
        """
        return RedisRouter(settings.REDIS_HOST, settings.REDIS_PORT,
                           REDIS_DEFAULT_DB, settings.REDIS_PREFIX)

    def __init__(self, host, port, db, prefix):
        self.client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
        self.prefix = prefix

    def _prefixed_route_key(self, source):
        """
        Returns the prefixed key, if prefix has been defined, for the given
        route.
        """
        prefixed_key = f'routes:{source}'
        if self.prefix is not None:
            prefixed_key = f'{self.prefix}:{prefixed_key}'
        
        return prefixed_key

    def lookup(self, host, path=None, silent=False):
        """
        Fetches the target host for the given host name and path. If no host matching
        the given name is found and silent is False, raises a LookupNotFound exception.
        """
        lookup_host = self._prefixed_route_key(host)
        path = path or '/'

        target_host = self.client.hget(lookup_host, path)
        if target_host is None and not silent:
            raise RedisRouter.LookupNotFound(
                'Given host does not match with any route'
            )
        else:
            return target_host
    
    def lookup_paths(self, host):
        """
        Fetches the (path, target) pairs for the given host, returning
        a dict of the key -> value pairs
        """
        lookup_host = self._prefixed_route_key(host)
        return self.client.hgetall(lookup_host)

    def lookup_hosts(self, pattern):
        """
        Fetches hosts that match the given pattern. If no pattern is given,
        all hosts are returned.
        """
        if not pattern:
            pattern = '*'
        lookup_pattern = self._prefixed_route_key(pattern)
        keys = self.client.keys(lookup_pattern)
        return [key[len(lookup_pattern) - len(pattern):] for key in keys]

    def lookup_routes(self, pattern):
        """
        Fetches routes with host that matches the given pattern. If no pattern
        is given, all routes are returned.
        """
        hosts = self.lookup_hosts(pattern)
        routes = []
        for host in hosts:
            routes.append(
                {
                    'host': host,
                    'paths': self.lookup_paths(host)
                }
            )
        return routes

    def insert(self, host, path, target):
        """
        Inserts a new host/path -> target entry in to the database.
        """
        host_key = self._prefixed_route_key(host)
        self.client.hset(host_key, path, target)
    
    def update_path(self, host, old_path, new_path, target):
        """
        Updates a path -> target mapping
        """
        host_key = self._prefixed_route_key(host)
        
        if self.client.hexists(host, new_path) > 0:
            raise RedisRouter.PathExists()
        
        pipe = self.client.pipeline()
        if old_path != new_path:
            pipe.mdel(host_key, old_path)
        pipe.msetnx(host_key, new_path, target)
        pipe.execute()
    
    def update_host(self, old_host, new_host):
        """
        Updates a host in the database
        """
        old_key = self._prefixed_route_key(old_host)
        new_key = self._prefixed_route_key(new_host)
        
        if self.client.exists(new_key) > 0:
            raise RedisRouter.HostExists()

        self.client.renamenx(old_key, new_key)

    def delete_path(self, host, path):
        """
        Deletes the entry of the given path, if it exists.
        """
        host_key = self._prefixed_route_key(host)
        self.client.hdel(host_key, path)
    
    def delete_host(self, host):
        """
        Deletes the entry of the given host, if it exists.
        """
        host_key = self._prefixed_route_key(host)
        self.client.delete(host_key)


class RedisUsers:
    """
    Users db using a redis backend
    """
    class UserNotFound(Exception):
        """
        Exception raised when a lookup for a specific user was not found.
        """
        pass

    @staticmethod
    def from_config(path=None):
        """
        Returns a RedisUsers, using the default configuration from Ceryx
        settings.
        """
        return RedisUsers(settings.REDIS_HOST, settings.REDIS_PORT,
                          REDIS_DEFAULT_DB, settings.REDIS_PREFIX)

    def __init__(self, host, port, db, prefix):
        self.client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
        self.prefix = prefix

    def _prefixed_key(self, username):
        """
        Returns the prefixed key, if prefix has been defined, for the given user.
        """
        prefixed_key = f'users:{username}'
        if self.prefix is not None:
            prefixed_key = f'{self.prefix}:{prefixed_key}'
        
        return prefixed_key
    
    def login(self, username, plain_password):
        key = self._prefixed_key(username)
        password = self.client.get(key)

        if not password:
            return False

        password = password.encode()
        plain_password = plain_password.encode()

        return bcrypt.checkpw(plain_password, password)

    def lookup(self, pattern=None):
        pattern = pattern or '*'
        lookup_pattern = self._prefixed_key(pattern)
        keys = self.client.keys(lookup_pattern)
        return [key[len(lookup_pattern) - len(pattern):] for key in keys]
    
    def insert(self, username, plain_password):
        hashed_password = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt())
        password = hashed_password.decode('utf-8')

        key = self._prefixed_key(username)
        self.client.set(key, password)

    def delete(self, username):
        key = self._prefixed_key(username)
        self.client.delete(key)
