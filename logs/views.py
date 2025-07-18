from django.shortcuts import render
from .forms import LogUploadForm
from .models import LogEntry
import csv
import io
from datetime import datetime

def upload_logs(request):
    logs = []
    anomalies = []
    if request.method == 'POST':
        form = LogUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            decoded = file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded))
            for row in reader:
                is_anomaly = 'error' in row['message'].lower() or row['level'].lower() == 'critical'
                log = LogEntry.objects.create(
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    level=row['level'],
                    message=row['message'],
                    source=row['source'],
                    is_anomaly=is_anomaly,
                )
                logs.append(log)
                if is_anomaly:
                    anomalies.append(log)
    else:
        form = LogUploadForm()

    return render(request, 'upload_logs.html', {
        'form': form,
        'logs': logs,
        'anomalies': anomalies
    })
