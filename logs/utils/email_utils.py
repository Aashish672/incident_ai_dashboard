import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_anomaly_alert(log_entry):
    """Send an anomaly alert email to the log uploader, their admin, and/or a fallback."""
    subject = f"🚨 Anomaly Detected: {log_entry.level}"
    message = (
        f"An anomaly has been detected in the system.\n\n"
        f"Timestamp: {log_entry.timestamp}\n"
        f"Source:    {log_entry.source}\n"
        f"Level:     {log_entry.level}\n"
        f"Message:   {log_entry.message}\n"
    )

    recipient_list = []

    # 1. Add the log uploader's email
    if log_entry.user and log_entry.user.email:
        recipient_list.append(log_entry.user.email)

    # 2. Add the admin's email assigned to this user
    try:
        admin_user = log_entry.user.profile.admin
        if admin_user and admin_user.email and admin_user.email not in recipient_list:
            recipient_list.append(admin_user.email)
    except Exception:
        pass

    # 3. Fallback to configured alert email
    if not recipient_list:
        fallback = getattr(settings, "ALERT_RECIPIENT_EMAIL", "")
        if fallback:
            recipient_list.append(fallback)

    if not recipient_list:
        logger.warning("No recipients for anomaly alert on log %d", log_entry.id)
        return

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        logger.info("Anomaly alert sent to %s for log %d", recipient_list, log_entry.id)
    except Exception:
        logger.exception("Failed to send anomaly alert for log %d", log_entry.id)
