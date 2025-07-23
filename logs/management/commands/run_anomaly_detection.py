from django.core.management.base import BaseCommand
from scripts.log_processor import preprocess_and_detect_anomalies

class Command(BaseCommand):
    help='Run anomaly detection on logs'

    def handle(self,*args,**kwargs):
        print("Starting scheduled anomaly detection...")
        preprocess_and_detect_anomalies()
        print("Anomaly detection complete.")