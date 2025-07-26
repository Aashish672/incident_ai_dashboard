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
from django.urls import reverse_lazy


urlpatterns = [
    path('admin/', admin.site.urls),

    # Landing page at root
    

    # Auth: login, logout, register
    path('login/', auth_views.LoginView.as_view(
             template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),

    path('register/', log_views.register, name='register'),

    # Password reset flow
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='auth/password_reset.html',
             email_template_name='auth/password_reset_email.txt',
             subject_template_name='auth/password_reset_subject.txt',
             success_url=reverse_lazy('password_reset_done')
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='auth/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='auth/password_reset_confirm.html',
             success_url=reverse_lazy('password_reset_complete')
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='auth/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # Password change (logged-in users)
    path('password-change/',
         auth_views.PasswordChangeView.as_view(
             template_name='auth/password_change.html',
             success_url=reverse_lazy('password_change_done')
         ),
         name='password_change'),
    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='auth/password_change_done.html'
         ),
         name='password_change_done'),

         #Profile
         path('profile/',log_views.profile_view,name='profile'),
    # Your app urls under /logs/
    path('', log_views.landing_page, name='landing'),
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



