import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from logs.models import LogEntry
class Command(BaseCommand):
    help="Load sample log entries into the database"
     
    def handle(self,*args,**kwargs):
        log_levels=['INFO','WARNING','ERROR','DEBUG','CRITICAL']
        sources=['server-1','server-2','auth-service','db','api-gateway']
        messages=[
            "User login successful.",
            "Database connection failed.",
            "Memory usage exceeded threshold.",
            "Disk space running low.",
            "Error parsing JSON request.",
            "Cache miss for key: user_profile_123",
            "Unexpected token in config file.",
            "User session timed out.",
            "Email service not responding.",
            "Backup completed successfully."
        ]

        for _ in range(50):
            log=LogEntry(
                timestamp=timezone.now(),
                log_level=random.choice(log_levels),
                source=random.choice(sources),
                message=random.choice(messages),
                is_anomaly=random.choice([False,False,False,True])
            )
            log.save()
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded 50 sample log entries.'))