import csv
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime
from logs.models import LogEntry

class Command(BaseCommand):
    help = 'Load log entries from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file']
        if not file_path:
            raise CommandError("Please provide a CSV file using --file")

        try:
            with open(file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    timestamp = parse_datetime(row['timestamp'])
                    log_level = row['log_level']
                    source = row['source']
                    message = row['message']

                    LogEntry.objects.create(
                        timestamp=timestamp,
                        log_level=log_level,
                        source=source,
                        message=message,
                        is_anomaly=False
                    )
                    count += 1

                self.stdout.write(self.style.SUCCESS(f'✅ Imported {count} log entries from {file_path}'))

        except Exception as e:
            raise CommandError(f"❌ Failed to load logs: {str(e)}")
