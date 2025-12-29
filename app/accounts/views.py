import socket
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import User, LoginLog
from . import services


@csrf_exempt
def signup(request):
    """회원가입 뷰"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # 유효성 검사
        if not username or not password:
            return render(request, 'accounts/signup.html', {
                'error': '아이디와 비밀번호를 입력해주세요.',
                'hostname': socket.gethostname()
            })

        # 중복 확인
        if services.is_username_taken(username):
            return render(request, 'accounts/signup.html', {
                'error': '이미 존재하는 아이디입니다.',
                'hostname': socket.gethostname()
            })

        # 사용자 생성
        services.create_user(username, password)
        return redirect('accounts:login')

    return render(request, 'accounts/signup.html', {
        'hostname': socket.gethostname()
    })


@csrf_exempt
def login(request):
    """로그인 뷰"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # 유효성 검사
        if not username or not password:
            return render(request, 'accounts/login.html', {
                'error': '아이디와 비밀번호를 입력해주세요.',
                'hostname': socket.gethostname()
            })

        # 인증
        user = services.authenticate(username, password)
        if not user:
            return render(request, 'accounts/login.html', {
                'error': '아이디 또는 비밀번호가 올바르지 않습니다.',
                'hostname': socket.gethostname()
            })

        # 세션에 사용자 정보 저장
        request.session['user_id'] = user.id
        request.session['username'] = user.username

        # 로그인 기록 저장
        services.create_login_log(user)

        return redirect('index')

    return render(request, 'accounts/login.html', {
        'hostname': socket.gethostname()
    })


def logout(request):
    """로그아웃 뷰"""
    request.session.flush()
    return redirect('index')


def login_logs(request):
    """로그인 기록 조회 API"""
    logs = LoginLog.objects.all().order_by('-login_at')[:50]
    return JsonResponse({
        'logs': [
            {
                'username': log.username,
                'login_at': str(log.login_at),
                'server_hostname': log.server_hostname
            }
            for log in logs
        ],
        'hostname': socket.gethostname()
    })
