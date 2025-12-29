from django.db import models


class User(models.Model):
    """사용자 모델 (CrateDB doc.users 테이블과 매핑)"""
    id = models.TextField(primary_key=True)
    username = models.TextField(unique=True)
    password = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False  # Django 마이그레이션 사용 안 함
        db_table = 'doc"."users'  # CrateDB 스키마.테이블 형식

    def __str__(self):
        return self.username


class LoginLog(models.Model):
    """로그인 기록 모델 (CrateDB doc.login_logs 테이블과 매핑)"""
    id = models.TextField(primary_key=True)
    user_id = models.TextField()
    username = models.TextField()
    login_at = models.DateTimeField(auto_now_add=True)
    server_hostname = models.TextField(null=True)

    class Meta:
        managed = False  # Django 마이그레이션 사용 안 함
        db_table = 'doc"."login_logs'  # CrateDB 스키마.테이블 형식

    def __str__(self):
        return f"{self.username} - {self.login_at}"
