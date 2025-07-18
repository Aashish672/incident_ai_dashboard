from django.db import models

# Create your models here.
LOG_LEVEL_CHOICES=[
    ('INFO','Info'),
    ('WARNING','Warning'),
    ('ERROR','Error'),
    ('DEBUG','Debug'),
    ('CRITICAL','Critical'),
]

class LogEntry(models.Model):
    timestamp=models.DateTimeField()
    level=models.CharField(max_length=10,choices=LOG_LEVEL_CHOICES)
    message=models.TextField()
    source=models.CharField(max_length=255,blank=True,null=True)
    is_anomaly=models.BooleanField(default=False)
     
    def __str__(self):
        return f"[{self.timestamp}]{self.level}-{self.message[:50]}"