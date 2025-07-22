# utils/email_utils.py

from django.core.mail import send_mail
from django.conf import settings

def send_anomaly_alert(log_entry):
    subject = f"🚨 Anomaly Detected: {log_entry.level}"
    message = f"""
An anomaly has been detected in the system.

Timestamp: {log_entry.timestamp}
Source: {log_entry.source}
Level: {log_entry.level}
Message: {log_entry.message}
    """
    recipient_list = ['38aashishkumarsingh11a@gmail.com']  # 🔁 Replace with your email

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )
