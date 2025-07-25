from django.urls import path
from . import views

app_name = 'logs'

urlpatterns = [
    path('', views.log_list, name='log_list'),  # list logs - /logs/
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('upload/', views.upload_logs, name='upload_logs'),
    path('detail/<int:pk>/', views.log_detail, name='log_detail'),
    path('export/', views.export_logs_csv, name='export_logs_csv'),
    path('export/anomalies/', views.export_anomalies_csv, name='export_anomalies'),
]
