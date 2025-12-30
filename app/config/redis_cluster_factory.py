"""
Redis Cluster Connection Factory for django-redis
django-redis의 Connection Factory를 오버라이드하여 RedisCluster 사용
"""
from django_redis.pool import ConnectionFactory
from redis.cluster import RedisCluster, ClusterNode


class RedisClusterConnectionFactory(ConnectionFactory):
    """
    django-redis에서 Redis Cluster를 사용하기 위한 커스텀 Connection Factory
    """

    def __init__(self, options):
        # 기본 ConnectionFactory 초기화는 건너뛰고 직접 처리
        self._pool = None
        self._client = None
        self._options = options

    def connect(self, url):
        """
        Redis Cluster에 연결하고 클라이언트 반환
        """
        if self._client is None:
            startup_nodes = [
                ClusterNode('172.28.0.21', 7001),
                ClusterNode('172.28.0.22', 7002),
                ClusterNode('172.28.0.23', 7003),
            ]

            self._client = RedisCluster(
                startup_nodes=startup_nodes,
                decode_responses=False,
                skip_full_coverage_check=True,
            )

        return self._client

    def disconnect(self, connection):
        """
        연결 종료
        """
        if self._client:
            self._client.close()
            self._client = None

    def get_connection(self, params):
        """
        ConnectionFactory 인터페이스 구현
        """
        return self.connect(None)
