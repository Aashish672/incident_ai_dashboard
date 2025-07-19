from django.shortcuts import render
from .forms import LogUploadForm
from .models import LogEntry
import csv
import io
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime


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


def log_list(request):
    logs=LogEntry.objects.all().order_by('-timestamp')

    level=request.GET.get('level')
    show_anomalies=request.GET.get('anomaly')=='true'
    start_date=request.GET.get('start')
    end_date=request.GET.get('end')
    search_query=request.GET.get('search','').strip()

    if show_anomalies:
        logs=logs.filter(is_anomaly=True)
    
    if level:
        logs=logs.filter(level=level)

    if start_date and end_date:
        logs=logs.filter(timestamp__range=[start_date,end_date])
    
    if search_query:
        logs=logs.filter(Q(message__icontains=search_query) | Q(source__icontains=search_query))

    paginator=Paginator(logs,10)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)

    return render(request,'log_list.html',{'page_obj':page_obj})

def export_logs_csv(request):
    logs=LogEntry.objects.all().order_by('-timestamp')

    level=request.GET.get('level')
    show_anomalies=request.GET.get('anomaly')=='true'
    start_date=request.GET.get('start')
    end_date=request.GET.get('end')

    if level:
        logs=logs.filter(level=level)

    if show_anomalies:
        logs=logs.filter(is_anomaly=True)

    if start_date:
        logs=logs.filter(timestamp__date__gte=start_date)

    if end_date:
        logs=logs.filter(timestamp__date__lte=end_date)

    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename="filtered_logs.csv"'

    writer=csv.writer(response)
    writer.writerow(['Timestamp','Level','Message','Source','Anomaly'])

    for log in logs:
        writer.writerow([log.timestamp,log.level,log.message,log.source,log.is_anomaly])

    return response