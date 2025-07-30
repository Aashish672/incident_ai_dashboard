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

    recipient_list = []

    # 1. Add the log uploader's email (if exists)
    if log_entry.user and log_entry.user.email:
        recipient_list.append(log_entry.user.email)

    # 2. Add the admin's email assigned to this user (if different and exists)
    try:
        admin_user = log_entry.user.profile.admin
        if admin_user and admin_user.email and admin_user.email not in recipient_list:
            recipient_list.append(admin_user.email)
    except Exception:
        # Profile or admin might not exist; ignore silently or log if you want
        pass

    # If no recipients, fallback to a default email (optional)
    if not recipient_list:
        recipient_list = ['38aashishkumarsingh11a@gmail.com']  # your fallback email

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )
