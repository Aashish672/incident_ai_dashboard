from django.urls import path
from . import views

urlpatterns = [
    path('',views.log_list,name='log_list'),
    path('upload/', views.upload_logs, name='upload_logs'),
    path('logs/<int:pk>',views.log_detail,name='log_detail'),
    path('logs/export/',views.export_logs_csv,name='export_logs_csv'),
    path('dashboard/',views.dashboard_view,name='dashboard'),
    path('export/anomalies/',views.export_anomalies_csv,name='export_anomalies')
]
