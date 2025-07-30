from django.db import models
from django.contrib.auth.models import User

LOG_LEVEL_CHOICES = [
    ('INFO', 'Info'),
    ('WARNING', 'Warning'),
    ('ERROR', 'Error'),
    ('DEBUG', 'Debug'),
    ('CRITICAL', 'Critical'),
]


class LogEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='logs_log_entries')  # <-- ADDED related_name
    timestamp = models.DateTimeField()
    level = models.CharField(max_length=10, choices=LOG_LEVEL_CHOICES)
    message = models.TextField()
    source = models.CharField(max_length=255, blank=True, null=True)
    is_anomaly = models.BooleanField(default=False)
    alert_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.timestamp}]{self.level}-{self.message[:50]}"
    

class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('viewer', 'Viewer'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')
    admin = models.ForeignKey(
        User,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='viewers',
        limit_choices_to={'profile__role': 'admin'},
        help_text="Assign the admin this viewer reports to",
    )

    def __str__(self):
        return f"{self.user.username}-{self.role}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.role == "admin" and self.admin is not None:
            raise ValidationError("Admins cannot have an admin assigned.")
        if self.role == "viewer" and self.admin is None:
            raise ValidationError("Viewers must be assigned to an admin.")

class Notification(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="notifications")
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    is_read=models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:30]}"