# Django Load Balancing Cluster

이 프로젝트는 Django 애플리케이션을 여러 개의 컨테이너로 띄우고, Nginx를 사용하여 부하 분산(Load Balancing)을 구현한 예제 프로젝트입니다.

## 시스템 아키텍처
1. Nginx (Load Balancer): 포트 8888로 들어오는 모든 요청을 받아 3개의 Django 컨테이너로 분산합니다.
2. Django Nodes (Web1, Web2, Web3): 실제 비즈니스 로직을 처리하는 애플리케이션 서버입니다. 각 노드는 자신의 호스트네임을 식별하여 응답에 포함합니다.
3. CrateDB Cluster: 3개의 노드로 구성된 분산 데이터베이스 클러스터입니다.

## 프로젝트 구조
- app/: Django 프로젝트 소스 코드
    - config/: Django 프로젝트 설정
    - core/: 메인 로직 앱 (API 및 UI)
    - Dockerfile: Django 컨테이너 빌드 명세서
- nginx/: Nginx 설정 파일
    - nginx.conf: 4가지 로드 밸런싱 알고리즘이 미리 정의되어 있음
- docker-compose.yml: 전체 서비스(Nginx + Django 3개 + CrateDB 3개) 구성 및 실행 정의

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

## 향후 계획 (Next Steps)

### 1. 회원가입 및 로그인 구현
- **회원가입**: 간단한 회원가입 기능 구현 및 DB 저장
- **로그인 기록**: 로그인 성공 시 로그인 기록 저장

### 2. 세션 클러스터링 (Session Clustering)
- **목표**: Nginx 로드 밸런싱의 Least Connections (최소 연결 기반) 알고리즘 환경에서도 로그인 상태 유지
- **Redis 적용**: 로그인 세션 저장소로 Redis 사용하여 세션 공유 구현