from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_logs, name='upload_logs'),
]
