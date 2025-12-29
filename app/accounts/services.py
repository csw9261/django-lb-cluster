import hashlib
import uuid
import socket
from .models import User, LoginLog


def hash_password(password: str) -> str:
    """비밀번호를 SHA-256으로 해시"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """비밀번호 검증"""
    return hash_password(password) == hashed


def create_user(username: str, password: str) -> User:
    """새 사용자 생성"""
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        password=hash_password(password)
    )
    user.save()
    return user


def authenticate(username: str, password: str) -> User | None:
    """사용자 인증 (성공 시 User 반환, 실패 시 None)"""
    try:
        user = User.objects.get(username=username)
        if verify_password(password, user.password):
            return user
    except User.DoesNotExist:
        pass
    return None


def create_login_log(user: User) -> LoginLog:
    """로그인 기록 생성"""
    log = LoginLog(
        id=str(uuid.uuid4()),
        user_id=user.id,
        username=user.username,
        server_hostname=socket.gethostname()
    )
    log.save()
    return log


def is_username_taken(username: str) -> bool:
    """사용자명 중복 확인"""
    return User.objects.filter(username=username).exists()
