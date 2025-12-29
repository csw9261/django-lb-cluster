-- CrateDB 테이블 초기화 스크립트
-- 사용법: CrateDB Admin UI (http://127.0.0.1:4200) 콘솔에서 실행
-- 참고: CrateDB는 Lucene 기반으로 모든 컬럼이 자동 인덱싱됨

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS doc.users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 로그인 기록 테이블
CREATE TABLE IF NOT EXISTS doc.login_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    username TEXT NOT NULL,
    login_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    server_hostname TEXT
);

-- Django 세션 테이블
CREATE TABLE IF NOT EXISTS doc.django_session (
    session_key TEXT PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP NOT NULL
);
