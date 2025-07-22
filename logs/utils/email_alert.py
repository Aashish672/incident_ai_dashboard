from django.core.mail import send_mail
from django.conf import settings

def send_anomaly_alert(log):
    subject=f"Anomaly Detected: {log.level}"
    message=(f"An anomaly has been detected in the logs:\n\n"
             f"Timestamp: {log.timestamp}\n"
             f"Level: {log.level}\n"
             f"Source: {log.source}\n"
             f"Message: {log.message}"
             )
    from_email=settings.DEFAULT_FROM_EMAIL
    recipient_list=['38aashishkumarsingh11a@gmail.com']
    send_mail(subject,message,from_email,recipient_list)