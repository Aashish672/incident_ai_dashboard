"""
URL configuration for incident_ai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from logs import views as log_views
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    # Landing page at root
    path('', log_views.landing_page, name='landing'),

    # Auth: login, logout, register
    path('login/', auth_views.LoginView.as_view(
             template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),

    path('register/', log_views.register, name='register'),

    # Your app urls under /logs/
    path('logs/', include('logs.urls')),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    # path('register/', log_views.register, name='register'),
    # path('', auth_views.LoginView.as_view(template_name='auth/login.html')),
    # # your app urls
    # path('logs', include('logs.urls')),

    # Redirect default root to 'upload_logs' if needed, 
    # but only if 'upload_logs' is a named URL in logs.urls
    #path('', lambda request: redirect('upload_logs')),  # This conflicts with the above line



