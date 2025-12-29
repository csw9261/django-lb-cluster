from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # 회원 관련
    path('', include('core.urls')),  # 루트 경로 포함
]