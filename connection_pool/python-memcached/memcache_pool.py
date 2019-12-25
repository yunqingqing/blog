import collections
import contextlib
import logging
from six.moves import queue

import memcache


LOG = logging.getLogger(__name__)
_PoolItem = collections.namedtuple('_PoolItem', ['ttl', 'connection'])

class ConnectionPool(queue.Queue):
    def __init__(self, maxsize, unused_timeout, conn_get_timeout=None):
        queue.Queue.__init__(self, maxsize)
        self._unuse_timeout = unused_timeout
        self._connection_get_timeout = conn_get_timeout
        self._acquired = 0
        self._LOG = logging.getLogger(__name__)


    def _create_connection(self):
        raise NotImplementedError

    def _destroy_connection(self):
        raise NotImplementedError

    def _debug_logger(self, msg, *args, **kwargs):
        if LOG.isEnabledFor(logging.DEBUG):
            thread_id = threading.current_thread().ident
            args = (id(self), thread_id) + args
            prefix = "Memcached pool %s, thread %s: "
            LOG.debug(prefix + msg, *args, **kwargs)

    def _drop_expired_connections(self):
        now = time.time()
        try:
            while self.queue[0].ttl < now:
                con = self.queue.popleft().connection
                self._debug_logger('Reaping connection %s', id(conn))
                self._destroy_connection(conn)
        except IndexError:
            pass

    @contextlib.contextmanager
    def acquire(self):
        self._drop_expired_connections()
        try:
            conn = self.get(timeout=self._connection_get_timeout)
        except queue.Empty:
            self._LOG.critical("Unable to get connection from pool id "
                               "%(id)s after %(second)s seconds.", 
                               {"id": id(self),
                                "seconds": self._connection_get_timeout})

        try:
            yield conn
        finally:
            try:
                queue.Queue.put(self, conn, block=False)
            except queue.Full:
                self._destroy_connection(conn)

    def _get(self):
        try:
            conn = self.queue.pop().connection
        except IndexError:
            conn = self._create_connection()
        self._acquired += 1
        return conn
    
    def _put(self, conn):
        self.queue.append(_PoolItem(
            ttl=time.time() + self._unuse_timeout,
            connection=conn
        ))
        self._acquired -= 1


class MemcacheClientPool(ConnectionPool):
    def __init__(self, urls, arguments, **kwargs):
        ConnectionPool.__init__(self, **kwargs)
        self.urls = urls
        self._arguments = arguments
        self._hosts_deaduntil = [0] * len(urls)

    def _create_connection(self):
        return memcache.Client(self.urls, **self._arguments)

    def _destroy_connection(self, conn):
        conn.disconnect_all()

    def _get(self):
        conn = ConnectionPool._get(self)
        try:
            now = time.time()
            for deaduntil, host in zip(self._hosts_deaduntil, conn.servers):
                if host.deaduntil <= now < deaduntil:
                    host.mark_dead('propagating death mark for the pool')
                host.deaduntil = deaduntil
        except Exception:
            ConnectionPool._put(self, conn)
        return conn

    def _put(self, conn):
        try:
            now = time.time()
            for i, host in zip(itertools.count(), conn.servers):
                deaduntil = self._hosts_deaduntil[i]
                if deaduntil <= now:
                    if host.deaduntil > now:
                        self._hosts_deaduntil[i] = host.deaduntil
                        self._debug_logger("marked host %s dead until %s",
                                           self.urls[i], host.deaduntil)
                    else:
                        self._hosts_deaduntil[i] = 0

            if all(deaduntil > now for deaduntil in self._hosts_deaduntil):
                self._debug_logger('all hosts are')
                self._hosts_deaduntil[:] = [0] * len(self._hosts_deaduntil)
        finally:
            ConnectPool._put(self, conn)

class PoolClient():
    def __init__(self, memcache_servers, memcache_dead_retry=None,
                 memcache_pool_maxsize=None, memcache_pool_unused_timeout=None,
                 memcahce_pool_conn_get_timeout=None,
                 memcache_pool_socket_timeout=None):
        self.pool = MemcacheClientPool(
            memcache_servers,
            arguments={
                'dead_retry': memcache_dead_retry,
                'socket_timeout': memcache_pool_socket_timeout
            },
            maxsize=memcache_pool_maxsize,
            unused_timeout=memcache_pool_unused_timeout,
            conn_get_timeout=memcahce_pool_conn_get_timeout
        )

    @contextlib.contextmanager
    def reserve(self):
        with self.pool.get() as client:
            yield client

class CacheManager():
    def __init__(self, memcache_servers, memcache_dead_retry=None,
                 memcache_pool_maxsize=None, memcache_pool_unused_timeout=None,
                 memcahce_pool_conn_get_timeout=None,
                 memcache_pool_socket_timeout=None):
        self._pool = PoolClient(
            memcache_servers,
            memcache_dead_retry=memcache_dead_retry,
            memcache_pool_socket_timeout=memcache_pool_socket_timeout,
            memcache_pool_maxsize=memcache_pool_maxsize,
            memcache_pool_unused_timeout=memcache_pool_unused_timeout,
            memcahce_pool_conn_get_timeout=memcahce_pool_conn_get_timeout
        )

    def get(self, key):
        import pdb;pdb.set_trace()
        with self._pool.reserve() as client:
            result = client.get(key)
        return result

if __name__ == "__main__":
    cache = CacheManager(["127.0.0.1:11211"], memcache_pool_maxsize=10, memcahce_pool_conn_get_timeout=10)
    print(cache.get("k1"))