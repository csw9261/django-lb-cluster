# Django Load Balancing Cluster

**13개의 Docker 컨테이너**로 구성된 고가용성 분산 시스템 예제 프로젝트입니다.

```
Nginx (Load Balancer)
    ├── Django × 3 (Application)
    ├── Redis Cluster × 6 (Session Store: Master 3 + Replica 3)
    └── CrateDB Cluster × 3 (Data Store)
```

- **Nginx**: 4가지 로드밸런싱 알고리즘 지원 (Round Robin, Least Conn, IP Hash, Weighted)
- **Redis Cluster**: 16384 해시 슬롯 분산, 마스터 장애 시 자동 페일오버
- **CrateDB Cluster**: 분산 SQL 데이터베이스, 자동 샤딩 및 복제
- **Django**: Gunicorn WSGI 서버, 세션 공유를 통한 Stateless 구성

## 시스템 아키텍처
1. Nginx (Load Balancer): 포트 8888로 들어오는 모든 요청을 받아 3개의 Django 컨테이너로 분산합니다.
2. Django Nodes (Web1, Web2, Web3): 실제 비즈니스 로직을 처리하는 애플리케이션 서버입니다. 각 노드는 자신의 호스트네임을 식별하여 응답에 포함합니다.
3. CrateDB Cluster: 3개의 노드로 구성된 분산 데이터베이스 클러스터입니다.
4. Redis Cluster: 6개의 노드(Master 3 + Replica 3)로 구성된 세션 저장소입니다.

## 프로젝트 구조
- app/: Django 프로젝트 소스 코드
    - config/: Django 프로젝트 설정
    - core/: 메인 로직 앱 (API 및 UI)
    - accounts/: 회원 관련 앱 (회원가입, 로그인, 로그아웃)
    - Dockerfile: Django 컨테이너 빌드 명세서
- nginx/: Nginx 설정 파일
    - nginx.conf: 4가지 로드 밸런싱 알고리즘이 미리 정의되어 있음
- redis/: Redis Cluster 설정 파일
    - redis.conf: 클러스터 모드 활성화 및 노드 설정
    - cluster-init.sh: 6개 노드를 클러스터로 구성하는 초기화 스크립트
- sql/: CrateDB 테이블 초기화 스크립트
- docker-compose.yml: 전체 서비스(Nginx + Django 3개 + CrateDB 3개 + Redis 6개) 구성 및 실행 정의

## 시작하기

### 사전 요구 사항
- Docker 및 Docker Compose 설치

### 서버 실행
프로젝트 루트 디렉토리에서 아래 명령어를 입력합니다.
```powershell
docker-compose up --build -d
```

### 접속 및 테스트
- 메인 UI: http://127.0.0.1:8888/
    - 현재 어느 서버 컨테이너에 연결되었는지 시각적으로 확인할 수 있습니다.
- JSON API: http://127.0.0.1:8888/api/hello/
    - {"message": "...", "hostname": "django-webX"} 형태의 데이터를 반환합니다.
- 회원가입: http://127.0.0.1:8888/accounts/signup/
- 로그인: http://127.0.0.1:8888/accounts/login/
- 로그인 기록: http://127.0.0.1:8888/accounts/logs/
- CrateDB Admin UI: http://127.0.0.1:4200/
    - 클러스터의 상태와 노드 정보를 대시보드에서 확인할 수 있습니다.

## Nginx 로드 밸런싱 알고리즘 테스트 방법
`nginx/nginx.conf` 파일에는 아래 4가지 알고리즘이 미리 정의되어 있습니다.
테스트를 원하면 `proxy_pass` 부분의 주석을 변경하고 `docker-compose restart nginx`를 실행하세요.

1. Round Robin (`django_round_robin`) - 기본값
2. Least Connections (`django_least_conn`)
3. IP Hash (`django_ip_hash`)
4. Weight (`django_weighted`)

## 주요 기능
- **CrateDB 클러스터링**: 3개의 노드로 구성된 분산 DB 환경을 구축하고 Django와 연동하였습니다.
- **로드 밸런싱**: Nginx를 통해 트래픽을 분산하고 부하를 관리합니다.
- **컨테이너 식별**: 각 응답이 어느 컨테이너에서 생성되었는지 추적 가능합니다.
- **컨테이너화**: 모든 인프라를 Docker 환경으로 구성하여 배포가 용이합니다.
- **서비스 의존성 관리**: CrateDB healthcheck를 통해 DB가 완전히 준비된 후 Django 서버가 시작됩니다.
- **회원 관리**: 회원가입, 로그인/로그아웃 기능 및 로그인 기록 조회를 제공합니다.
- **세션 관리**: Redis Cluster에 세션을 저장하여 로드 밸런싱 환경에서도 로그인 상태를 유지합니다.

## 서비스 시작 순서 (Healthcheck)
Django 컨테이너는 CrateDB가 완전히 준비될 때까지 대기한 후 시작됩니다.

```yaml
# CrateDB healthcheck 설정
healthcheck:
  test: ["CMD-SHELL", "crash --host crate-node1:4200 -c 'SELECT 1'"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s

# Django 컨테이너 의존성 설정
depends_on:
  crate-node1:
    condition: service_healthy
```

- `crash`: CrateDB 내장 CLI 도구로 실제 쿼리 실행 가능 여부를 확인합니다.
- `start_period`: 클러스터 초기화 시간(30초)을 고려하여 healthcheck 실패를 무시합니다.
- `service_healthy`: DB가 healthy 상태가 될 때까지 Django 컨테이너 시작을 대기합니다.

## CrateDB + Django 연동

### 호환성 이슈
CrateDB는 PostgreSQL 와이어 프로토콜을 지원하지만, Django의 PostgreSQL 백엔드와 완전히 호환되지 않습니다.
- Django 시작 시 마이그레이션 체크 과정에서 PostgreSQL 시스템 카탈로그(`pg_class`, `pg_namespace` 등)를 조회
- CrateDB는 해당 시스템 테이블을 지원하지 않아 `Schema 'crate' unknown` 에러 발생

### 해결 방법: Gunicorn 사용
Django 개발 서버(`runserver`) 대신 **Gunicorn**을 사용하여 마이그레이션 체크를 우회합니다.

```dockerfile
# Dockerfile
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8888"]
```

### Django ORM 사용 방식
- `models.py`는 ORM 쿼리 빌더 용도로만 사용
- 테이블 생성/변경은 CrateDB에서 직접 SQL로 수행
- Django 마이그레이션(`makemigrations`, `migrate`)은 사용하지 않음

## 세션 관리 (Session Management)

### 현재 구현 방식: Redis Cluster
Django 세션을 Redis Cluster에 저장하여 모든 Django 노드가 동일한 세션 정보를 공유합니다.
- **인메모리 저장**으로 빠른 세션 조회 (ms 단위)
- **TTL 자동 관리**로 만료된 세션 자동 삭제
- **고가용성**: 마스터 장애 시 레플리카가 자동 승격

## Redis Cluster + Django 연동

### 1. 개요
- **목표**: 더 빠른 세션 조회를 위해 Redis를 세션 저장소로 사용
- **장점**: 인메모리 저장으로 DB 부하 감소, TTL 자동 관리

#### Redis 추가 후 시스템 아키텍처

```
                                    ┌─────────────────┐
                                    │     Client      │
                                    │  (Browser/API)  │
                                    └────────┬────────┘
                                             │
                                             ▼ :8888
                                 ┌───────────────────────┐
                                 │        Nginx          │
                                 │    (Load Balancer)    │
                                 └───────────┬───────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
             ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
             │   Django    │          │   Django    │          │   Django    │
             │    Web1     │          │    Web2     │          │    Web3     │
             │  (Gunicorn) │          │  (Gunicorn) │          │  (Gunicorn) │
             └──────┬──────┘          └──────┬──────┘          └──────┬──────┘
                    │                        │                        │
                    └────────────────────────┼────────────────────────┘
                                             │
                        ┌────────────────────┴────────────────────┐
                        │                                         │
                        ▼                                         ▼
┌───────────────────────────────────────────────┐    ┌──────────────────────────────┐
│            Redis Cluster (Session Store)      │    │    CrateDB Cluster           │
│                  6 nodes                      │    │       (Data Store)           │
│                                               │    │                              │
│   ┌─────────────────────────────────────┐     │    │  ┌─────────┐                 │
│   │           Master Nodes              │     │    │  │ CrateDB │ :4200 (Admin)  │
│   │  ┌────────┐ ┌────────┐ ┌────────┐   │     │    │  │ Node 1  │ :5432 (PG)     │
│   │  │Master 1│ │Master 2│ │Master 3│   │     │    │  └─────────┘                 │
│   │  │ :7001  │ │ :7002  │ │ :7003  │   │     │    │                              │
│   │  │ Slots  │ │ Slots  │ │ Slots  │   │     │    │  ┌─────────┐  ┌─────────┐    │
│   │  │ 0-5460 │ │5461-   │ │10923-  │   │     │    │  │ CrateDB │  │ CrateDB │    │
│   │  │        │ │  10922 │ │  16383 │   │     │    │  │ Node 2  │  │ Node 3  │    │
│   │  └───┬────┘ └───┬────┘ └───┬────┘   │     │    │  └─────────┘  └─────────┘    │
│   └──────│──────────│──────────│────────┘     │    │                              │
│          │          │          │              │    │  ✓ 사용자 정보               │
│   ┌──────▼──────────▼──────────▼────────┐     │    │  ✓ 로그인 기록               │
│   │          Replica Nodes              │     │    │  ✓ 비즈니스 데이터           │
│   │  ┌────────┐ ┌────────┐ ┌────────┐   │     │    └──────────────────────────────┘
│   │  │Replica1│ │Replica2│ │Replica3│   │     │
│   │  │ :7004  │ │ :7005  │ │ :7006  │   │     │
│   │  │(M1복제) │ │(M2복제)│  │(M3복제)│   │     │
│   │  └────────┘ └────────┘ └────────┘   │     │
│   └─────────────────────────────────────┘     │
│                                               │
│  ✓ 16384 해시 슬롯을 3개 마스터가 분산 담당        │
│  ✓ 각 마스터는 자신의 레플리카에 데이터 복제        │
│  ✓ 마스터 장애 시 레플리카가 자동 승격             │
└───────────────────────────────────────────────┘
```

#### 데이터 흐름

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              요청 흐름                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. 로그인 요청                                                              │
│     Client ──▶ Nginx ──▶ Django(Web2) ──▶ CrateDB (사용자 인증)             │
│                                       ──▶ Redis   (세션 생성/저장)           │
│                                                                             │
│  2. 이후 요청 (세션 유지)                                                    │
│     Client ──▶ Nginx ──▶ Django(Web1) ──▶ Redis   (세션 조회) ✓ 빠름!       │
│                    │                                                        │
│                    └──▶ Django(Web3) ──▶ Redis   (동일 세션 공유)           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 현재 vs Redis 추가 후 비교

| 구분 | 현재 (DB 세션) | Redis 추가 후 |
|------|---------------|---------------|
| **세션 저장소** | CrateDB | Redis (인메모리) |
| **세션 조회 속도** | 디스크 I/O 발생 | 메모리 직접 조회 (ms 단위) |
| **DB 부하** | 세션 + 데이터 모두 처리 | 데이터만 처리 |
| **세션 만료** | 수동 관리 필요 | TTL 자동 만료 |
| **컨테이너 수** | 7개 (Nginx 1 + Django 3 + CrateDB 3) | 13개 (+Redis Cluster 6) |

#### Redis Cluster 설정 파일

**redis/redis.conf**
```conf
# 클러스터 모드 활성화
cluster-enabled yes

# 클러스터 구성 정보 저장 파일
cluster-config-file nodes.conf

# 노드 타임아웃 (밀리초) - 이 시간 동안 응답 없으면 장애로 판단
cluster-node-timeout 5000

# 데이터 지속성 (AOF 방식)
appendonly yes

# 모든 인터페이스에서 접속 허용
bind 0.0.0.0

# 보호 모드 비활성화 (개발 환경용)
protected-mode no
```

**redis/cluster-init.sh**
- 6개 Redis 노드가 모두 준비될 때까지 대기
- `redis-cli --cluster create` 명령으로 클러스터 구성
- `--cluster-replicas 1` 옵션으로 각 마스터당 1개의 레플리카 자동 할당
- 16384개의 해시 슬롯을 3개 마스터에 균등 분배

### 2. Docker에서 Redis Cluster 구성 시 주의사항

#### 문제: TTL exhausted 에러
Redis Cluster는 클라이언트에게 노드의 IP 주소를 반환합니다. Docker 환경에서는 내부 IP가 동적으로 할당되어 클라이언트가 해당 IP에 접근하지 못하는 문제가 발생합니다.

#### 해결: 고정 IP + cluster-announce-ip 설정

**docker-compose.yml**
```yaml
networks:
  app-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16

services:
  redis-node1:
    image: redis:latest
    command: >
      redis-server /usr/local/etc/redis/redis.conf
      --port 7001
      --cluster-announce-ip 172.28.0.21
      --cluster-announce-port 7001
      --cluster-announce-bus-port 17001
    networks:
      app-network:
        ipv4_address: 172.28.0.21
```

| 설정 | 설명 |
|------|------|
| `subnet` | Docker 네트워크에 고정 서브넷 할당 |
| `ipv4_address` | 각 Redis 노드에 고정 IP 할당 |
| `cluster-announce-ip` | 클라이언트에게 반환할 IP 주소 지정 |
| `cluster-announce-port` | 클라이언트 연결 포트 |
| `cluster-announce-bus-port` | 노드 간 통신 포트 (포트 + 10000) |

### 3. django-redis 호환성 문제 및 해결

#### 문제: django-redis + Redis Cluster 호환 불가
`django-redis`의 `DefaultClient`는 내부적으로 **pipeline**을 사용합니다. Redis Cluster에서는 같은 해시 슬롯에 있는 키만 하나의 pipeline에 담을 수 있어 `TTL exhausted` 에러가 발생합니다.

```python
# django-redis 내부 동작 (문제 발생 지점)
with self.client.pipeline() as pipe:
    pipe.exists(key)  # ← 다른 슬롯의 키면 MOVED 응답 → TTL exhausted
    pipe.get(key)
```

#### 해결: 커스텀 Connection Factory 작성
`redis-py`의 `RedisCluster`를 직접 사용하는 Connection Factory를 만들어 주입합니다.

**app/config/redis_cluster_factory.py**
```python
from django_redis.pool import ConnectionFactory
from redis.cluster import RedisCluster, ClusterNode

class RedisClusterConnectionFactory(ConnectionFactory):
    def __init__(self, options):
        self._pool = None
        self._client = None
        self._options = options

    def connect(self, url):
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
        if self._client:
            self._client.close()
            self._client = None

    def get_connection(self, params):
        return self.connect(None)
```

**app/config/settings.py**
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://172.28.0.21:7001/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_FACTORY': 'config.redis_cluster_factory.RedisClusterConnectionFactory',
        },
    }
}
```

### 4. Redis Cluster 확인 명령어

```powershell
# 클러스터 상태 확인
docker exec -it redis-node1 redis-cli -p 7001 cluster info

# 클러스터 노드 목록
docker exec -it redis-node1 redis-cli -p 7001 cluster nodes

# 각 노드별 저장된 키 확인 (키는 해시 슬롯에 따라 분산 저장됨)
docker exec -it redis-node1 redis-cli -p 7001 KEYS "*"
docker exec -it redis-node2 redis-cli -p 7002 KEYS "*"
docker exec -it redis-node3 redis-cli -p 7003 KEYS "*"

# 특정 키의 값 조회
docker exec -it redis-node3 redis-cli -p 7003 GET "키이름"

# 특정 키의 TTL(만료 시간) 확인
docker exec -it redis-node3 redis-cli -p 7003 TTL "키이름"
```

### 5. 트러블슈팅 요약

| 에러 | 원인 | 해결 |
|------|------|------|
| `TTL exhausted` | 클라이언트가 노드 IP에 접근 불가 | 고정 IP + `cluster-announce-ip` 설정 |
| `TTL exhausted` (설정 후에도) | django-redis pipeline 호환 문제 | 커스텀 Connection Factory 사용 |
| `RedisClusterException` | startup_nodes 미설정 | ClusterNode 객체로 노드 목록 전달 |
| `Relation unknown` | CrateDB 테이블 미생성 | `sql/init.sql` 스크립트 실행 |