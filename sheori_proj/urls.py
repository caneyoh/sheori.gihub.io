"""sheori URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# path()関数、include()関数のインポート
from django.urls import include, path
# 管理サイトの機能をインポート
from django.contrib import admin

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sheori.views.register import register_view, done_view


def index(request):
    contexts = {}
    return render(request, 'index.html', contexts)


urlpatterns = [
    path('', index, name='index'),  # 追加！
    # sheori アプリケーションの URL 設定を追加
    path('sheori/', include('sheori.urls')),
    # 管理サイト
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', register_view, name='register'),
    path('accounts/register/done', done_view, name='register_done'),
    # 追加ここまで
    path('sheori/', include('sheori.urls')),
]
