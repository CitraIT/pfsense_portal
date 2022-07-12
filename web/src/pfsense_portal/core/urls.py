"""pfsense_portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from .views import index, dashboard
from .views import login, logout_user
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', index, name='index'),
    # path('login', login, name='login'),
    path('login', LoginView.as_view(template_name='core/login.html'), name='login'),
    path('admin/', admin.site.urls),
    path('dashboard/', dashboard, name='dashboard'),
    path('accounts/', include('accounts.urls')),
    path('firewall/', include('firewall.urls')),
    path('backup/', include('backup.urls')),
    path('logout/', logout_user, name='logout'),
]
