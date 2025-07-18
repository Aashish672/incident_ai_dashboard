from django.core.management.base import BaseCommand
from logs.models import LogEntry
import csv
from datetime import datetime

class Command(BaseCommand):
    help = 'Load log entries from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file']
        if not file_path:
            self.stdout.write(self.style.ERROR("Please provide a file path using --file"))
            return

        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0

            for row in reader:
                # Ensure all keys are lowercase
                row = {k.lower(): v for k, v in row.items()}

                try:
                    is_anomaly = (
                        'error' in row.get('message', '').lower() or 
                        row.get('level', '').lower() == 'critical'
                    )

                    LogEntry.objects.create(
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        level=row['level'],
                        message=row['message'],
                        source=row['source'],
                        is_anomaly=is_anomaly
                    )
                    count += 1
                except KeyError as e:
                    self.stdout.write(self.style.ERROR(f"Missing column: {e}. Skipping row: {row}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error parsing row: {e}. Row data: {row}"))

            self.stdout.write(self.style.SUCCESS(f"✅ Loaded {count} log entries."))
