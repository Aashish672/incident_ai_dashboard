from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_logs, name='upload_logs'),
    path('logs/',views.log_list,name='log_list'),
    path('logs/export/',views.export_logs_csv,name='export_logs_csv',)
]
